#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

import asyncio
import logging
import sys
import time
from collections.abc import Callable, Coroutine, Hashable
from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any, ClassVar, Type, TypedDict, TypeVar

from bale.constants import ConversationFlowTarget

from .._exceptions import (FlowBadProtocolError, FlowBadStatusError,
                           FlowStateCorruptedError, FlowTimeoutError)
from .._utils.checkers import iscoroutinefunction, validate_timeout
from .._utils.typehint import MISSING, SentinelOrValue
from ..handlers import UpdateHandler
from ._step import Step

if TYPE_CHECKING:
    from ..context import Context
    from ..storage import BaseStorage

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

__all__ = ("FlowStatus", "ConversationFlow", "FlowTransition", "step")

_log = logging.getLogger(__name__)

END = object()
T = TypeVar("T")


class _StepDecoratorKwargs(TypedDict, total=False):
    name: str | None


class FlowStatus(IntEnum):
    NOT_STARTED = auto()
    PROCESSING_START = auto()
    WAITING_FOR_UPDATE = auto()
    PROCESSING_STEP = auto()
    COMPLETED = auto()
    PROCESSING_TIMEOUT = auto()
    TIMED_OUT = auto()


class FlowTransition:
    __slots__ = ("_target", "_timeout", "_invoke_handlers")

    def __init__(
        self,
        target: Any,
        timeout: SentinelOrValue[float | int] = MISSING,
        invoke_handlers: bool = False,
    ) -> None:
        if not isinstance(target, Step) and target is not END:
            raise TypeError("target must be a Step or END.")
        if not isinstance(invoke_handlers, bool):
            raise TypeError("invoke_handlers must be type of boolean.")
        if timeout is not MISSING and timeout is not None:
            if not isinstance(timeout, (float, int)):
                raise TypeError("timeout must be type if float or int.")
            if target is END:
                raise TypeError(
                    "Cannot end the conversion flow and use the timeout parameter at the same time."
                )

        self._target = target
        self._timeout = timeout
        self._invoke_handlers = invoke_handlers

    @property
    def target(self) -> Any:
        return self._target

    @property
    def timeout(self) -> SentinelOrValue[float | int]:
        return self._timeout

    @property
    def invoke_handlers(self) -> bool:
        return self._invoke_handlers


class ConversationMeta(type):
    def __new__(
        mcs,
        name: str,
        bases: tuple,
        namespace: dict,
        key: "Callable[[Context], Any] | ConversationFlowTarget" = ConversationFlowTarget.USER,
        **kwargs: Any,
    ):
        new_cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        new_cls.__default_timeout__ = kwargs.pop("timeout", MISSING)
        new_cls.__flow_key__ = key

        steps: dict[str, Step] = {}

        for base in reversed(new_cls.__mro__):
            for attr, value in base.__dict__.items():
                if attr in steps:
                    del steps[attr]

                is_staticmethod = isinstance(value, staticmethod)
                if is_staticmethod:
                    value = value.__func__
                if isinstance(value, Step):
                    if is_staticmethod:
                        raise TypeError(
                            f"Step in {base}.{attr!r} must not be staticmethod."
                        )

                    steps[attr] = value

        new_cls.__steps__ = steps
        return new_cls


class ConversationFlow(metaclass=ConversationMeta):
    """

    .. versionadded:: 3.0
    """

    END = END
    __steps__: ClassVar[dict[str, Step]]
    __default_timeout__: ClassVar[float | None]
    __flow_key__: ClassVar["Callable[[Context], Hashable] | ConversationFlowTarget"]

    __slots__ = (
        "_storage",
        "_steps",
        "_timeout",
        "_timeout_started_at",
        "_timeout_duration",
        "_timeout_task",
        "_status",
        "_status_lock",
        "_end_event",
        "_initial_key",
        "_flow_data",
    )

    def __init__(
        self,
        initial_key: Any,
        storage: "BaseStorage | None",
        timeout: SentinelOrValue[int | float] = MISSING,
    ) -> None:
        if not storage:
            raise RuntimeError(
                "Bot storage is not configured. "
                "A storage backend (e.g., MemoryStorage) must be attached to Bot object to manage conversation flows."
            )

        self._storage = storage
        self._initial_key = initial_key
        self._steps: dict[str, Step] = self.__steps__.copy()
        self._status: FlowStatus = FlowStatus.NOT_STARTED
        self._status_lock: asyncio.Lock = asyncio.Lock()
        self._end_event: asyncio.Event = asyncio.Event()

        if timeout is MISSING:
            timeout = self.__default_timeout__

        if not (timeout is None or timeout is MISSING):
            timeout = validate_timeout(timeout)

        for step in self._steps.values():
            step.bind(self)

        self._timeout: SentinelOrValue[float] = timeout

        self._timeout_duration: float | None = None
        self._timeout_started_at: float | None = None
        self._timeout_task: asyncio.Task[None] | None = None

        self._flow_data: dict[str, Any] = {}

    async def is_started(self) -> bool:
        async with self._status_lock:
            return self._status != FlowStatus.NOT_STARTED

    async def is_dead(self) -> bool:
        async with self._status_lock:
            return self._status in (FlowStatus.TIMED_OUT, FlowStatus.COMPLETED)

    def _get_storage_key(self) -> str:
        return self._initial_key

    async def _set_status(self, new_status: FlowStatus) -> None:
        async with self._status_lock:
            self._status = new_status

    @property
    def initial_key(self) -> Any:
        return self._initial_key

    def _is_our_record(self, record: Any) -> bool:
        return isinstance(record, dict) and record.get("flow") == self._identity()

    async def on_error(
        self, context: "Context", stp: Step, exc: Exception
    ) -> Any:  # noqa
        _log.exception(
            "Exception in %s (step: %s) Ignored. "
            "The conversation flow is cancelled by default in this function.",
            self,
            stp,
            exc_info=exc,
        )

    async def _process_error(
        self, context: "Context", step: Step, exc: Exception
    ) -> Any:
        try:
            return await self.on_error(context, step, exc)
        except Exception as _exc:
            _log.exception(
                "Exception raised in 'on_error' of %s while handling error in step %s",
                self,
                step,
                exc_info=_exc,
            )

        return None

    def get_data(self, field: str) -> Any:
        return self._flow_data.get(field)

    def set_data(self, field: str, value: Any) -> None:
        self._flow_data[field] = value

    def clear_data(self) -> Any:
        self._flow_data.clear()

    async def _drop_state(self, context: "Context") -> None:
        storage = self._storage
        await storage.drop_flow_data(self._initial_key)

    async def _get_current_step(self, context: "Context") -> "Step | None":
        storage = self._storage
        data = await storage.get_flow_data(self._initial_key)
        if data and self._is_our_record(data) and (stp_name := data.get("step")):
            return self._steps.get(stp_name or "")

        return None

    async def _set_current_step(self, context: "Context", next_step: "Step") -> None:
        storage = self._storage
        payload = self.build_payload(context, next_step)

        await storage.update_flow_data(self._initial_key, payload)

    def _get_step_name(self, target: Any) -> str | None:
        if isinstance(target, str):
            return target
        if isinstance(target, Step):
            for name, stp in self._steps.items():
                if stp is target or stp.func is target.func:
                    return name

        return None

    @classmethod
    def _identity(cls: Type["ConversationFlow"]) -> str:
        return f"{cls.__module__}.{cls.__qualname__}"

    async def _apply_timeout(self, ctx: "Context") -> None:
        self._status = FlowStatus.TIMED_OUT
        self._end_event.set()
        await self._drop_state(ctx)

    async def _apply_next_step(
        self,
        context: "Context",
        new_step: "Step",
        protocol_timeout: SentinelOrValue[float | int | None],
    ) -> None:
        async with self._status_lock:
            self._schedule_timeout(
                context,
                new_step,
                (
                    new_step.timeout
                    if protocol_timeout is MISSING
                    else (protocol_timeout or new_step.timeout)
                ),
            )
            await self._set_current_step(context, new_step)
            self._status = FlowStatus.WAITING_FOR_UPDATE

    async def _apply_end(self, ctx: "Context") -> None:
        self._status = FlowStatus.COMPLETED
        self._end_event.set()
        await self._drop_state(ctx)

    async def _apply_protocol(
        self,
        protocol: SentinelOrValue[FlowTransition | None],
        context: "Context",
        current_step: SentinelOrValue["Step | None"],
    ) -> bool:
        if not isinstance(protocol, FlowTransition):
            if protocol is None:
                if current_step in (MISSING, None):
                    _log.warning(
                        "Flow '%s' ended immediately: 'entry()' returned %r instead of a FlowTransition. "
                        "Did you forget to return 'self.transition(...)' ?",
                        self,
                        protocol,
                    )
                    protocol = FlowTransition(self.END, False)
                else:
                    protocol = FlowTransition(current_step, False)
            else:
                raise FlowBadProtocolError(protocol)

        target = protocol.target
        invoke_handlers = protocol.invoke_handlers
        timeout = protocol.timeout

        if isinstance(target, Step):
            if self._get_step_name(target) is None:
                raise FlowBadProtocolError(
                    protocol, "Step does not belong to this flow instance"
                )

            await self._apply_next_step(context, target, timeout)

        if target is self.END:
            async with self._status_lock:
                await self._apply_end(context)

        return invoke_handlers

    async def _run_handlers(self, context: "Context") -> None:
        bot = context.bot
        await bot.process_handlers(context)

    async def wait(self) -> None:
        async with self._status_lock:
            if self._status == FlowStatus.TIMED_OUT:
                raise FlowTimeoutError("Flow timed out.")
            if self._status == FlowStatus.COMPLETED:
                return

        await self._end_event.wait()

        async with self._status_lock:
            if self._status == FlowStatus.TIMED_OUT:
                raise FlowTimeoutError("Flow timed out.")

    def _schedule_timeout(
        self,
        context: "Context",
        step: "Step",
        step_duration: SentinelOrValue[float | int],
    ) -> None:
        bot = context.bot
        timeout = (
            self._timeout
            if step_duration is MISSING
            else (step_duration or self._timeout)
        )

        if timeout is not None and timeout is not MISSING:
            timeout: float | int

            self._timeout_duration = timeout
            self._timeout_started_at = time.time()
            self._timeout_task = bot.create_task(
                self._timeout_after(context, step, timeout)
            )

    async def _cancel_timeout(self) -> None:
        if task := self._timeout_task:
            if (
                isinstance(task, asyncio.Task)
                and task is not asyncio.current_task()
                and not task.done()
            ):
                task.cancel()

        self._timeout_duration = None
        self._timeout_started_at = None
        self._timeout_task = None

    async def _run_timeout_callback_safe(self, coro) -> Any:
        try:
            return await coro
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            _log.exception(
                "timeout callback processing failed for conversation flow %s",
                self,
                exc_info=exc,
            )

        return None

    async def _timeout_after(
        self, context: "Context", step: "Step", delay: float
    ) -> None:
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            _log.exception(
                "timeout processing failed for flow step %s", step, exc_info=exc
            )
            async with self._status_lock:
                await self._apply_end(context)
        else:
            async with self._status_lock:
                if self._status != FlowStatus.WAITING_FOR_UPDATE:
                    return

                current_step = await self._get_current_step(context)
                if current_step is not step:
                    return

                self._status = FlowStatus.PROCESSING_TIMEOUT

            protocol = MISSING

            timeout_callback: (
                Callable[["Context", "Step"], Coroutine[Any, Any, Any]] | None
            ) = getattr(self, "on_timeout", None)
            if timeout_callback is not None and iscoroutinefunction(timeout_callback):
                protocol = await self._run_timeout_callback_safe(
                    timeout_callback(step)
                )  # noqa

            if (
                protocol in (MISSING, None)
                or not isinstance(protocol, FlowTransition)
                or protocol.target in (MISSING, None)
                or not isinstance(protocol.target, Step)
                or self._get_step_name(protocol.target) is None
            ):
                async with self._status_lock:
                    await self._apply_timeout(context)
                return

            target = protocol.target
            invoke_handlers = protocol.invoke_handlers
            timeout = protocol.timeout
            await self._apply_next_step(context, target, timeout)
            if invoke_handlers:
                await self._run_handlers(context)

    async def invoke(self, ctx: "Context", *args) -> bool:
        async with self._status_lock:
            status = self._status
            if status == FlowStatus.NOT_STARTED:
                self._status = FlowStatus.PROCESSING_START
            elif status != FlowStatus.WAITING_FOR_UPDATE:
                raise FlowBadStatusError(status)

        if status == FlowStatus.NOT_STARTED:
            protocol = await self._run_entry(ctx, *args)
            return await self._apply_protocol(protocol, ctx, MISSING)

        current_step = await self._get_current_step(ctx)
        if current_step is None:
            async with self._status_lock:
                await self._apply_end(ctx)
            raise FlowStateCorruptedError(
                "Current step is missing or invalid in storage"
            )

        matched_args = await current_step.check_new_update(ctx)
        async with self._status_lock:
            if self._status != FlowStatus.WAITING_FOR_UPDATE:
                raise FlowBadStatusError(self._status)

        if matched_args is None:
            fallback_callback = getattr(self, "on_fallback", None)
            protocol = (
                await self.on_fallback(ctx, current_step) if fallback_callback else None
            )  # noqa
            if protocol is not None:
                return await self._apply_protocol(protocol, ctx, current_step)

            return False

        async with self._status_lock:
            if self._status != FlowStatus.WAITING_FOR_UPDATE:
                raise FlowBadStatusError(self._status)

            self._status = FlowStatus.PROCESSING_STEP
            await self._cancel_timeout()

        try:
            protocol = await current_step.handle_update(ctx, *matched_args)
        except Exception as exc:
            protocol = await self._process_error(ctx, current_step, exc)

            if protocol is None:
                async with self._status_lock:
                    await self._apply_end(ctx)

                raise

        invoke_handlers = await self._apply_protocol(protocol, ctx, current_step)
        return invoke_handlers

    async def _run_entry(self, context: "Context", *args) -> Any:
        return await self.entry(context, *args)

    async def _drop_storage(self, _: "Context") -> None:
        storage = self._storage
        await storage.drop_flow_data(self._initial_key)

    async def _delete(self, context: "Context") -> None:
        await self._cancel_timeout()
        await self._drop_storage(context)

    @classmethod
    def extract_key(cls, context: "Context") -> Any:
        flow_key = cls.__flow_key__
        if callable(flow_key):
            flow_key = flow_key(context)

        try:
            hash(flow_key)
        except TypeError as exc:
            raise TypeError("resolved flow key must be hashable") from exc

        return flow_key

    async def entry(self, context: "Context"):
        raise NotImplementedError(
            f"Flow '{type(self).__name__}' must implement 'entry(self, ctx)'."
        )

    def transition(
        self,
        next_step: Any,
        timeout: float | None = None,
        invoke_handlers: bool = False,
    ) -> "FlowTransition":
        return FlowTransition(next_step, timeout, invoke_handlers)

    def finish(self, invoke_handlers: bool = False) -> FlowTransition:
        return FlowTransition(self.END, invoke_handlers=invoke_handlers)

    @classmethod
    async def restore(
        cls: Type["ConversationFlow"],
        initial_key: str,
        storage: "BaseStorage | None",
        data: dict[str, Any],
    ) -> "ConversationFlow | None":
        data = data.copy()
        step_name: str | None = data.pop("step")
        timeout_started_at: float | None = data.pop("timeout_started_at")
        timeout_duration: float | None = data.pop("timeout_duration")
        flow_data: dict[str, Any] = data.pop("flow_data", {})

        if (
            timeout_duration is not None
            and timeout_started_at is not None
            and time.time() >= (timeout_started_at + timeout_duration)
        ):
            return None

        flow_instance = cls(initial_key, storage)
        flow_instance._flow_data = flow_data

        if step_name is not None:
            if step_name in flow_instance._steps:
                await flow_instance._set_status(FlowStatus.WAITING_FOR_UPDATE)
            else:
                return None

        return flow_instance

    def build_payload(self, context: "Context", next_step: Step) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "flow": self._identity(),
            "step": self._get_step_name(next_step),
        }
        if flow_data := self._flow_data:
            payload["flow_data"] = flow_data
        if self._timeout:
            payload["timeout_started_at"] = self._timeout_started_at  # noqa
            payload["timeout_duration"] = self._timeout_duration  # noqa

        return payload

    def __hash__(self) -> int:
        """:meta private:"""
        return hash((self.__class__, self._initial_key))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ConversationFlow):
            return (
                self._identity() == other._identity()
                and self._initial_key == other._initial_key
            )

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self._identity()


def step(
    handler: "UpdateHandler",
    timeout: SentinelOrValue[float | int | None] = MISSING,
    **kwargs: Unpack[_StepDecoratorKwargs],
):
    def wrapper(func):
        if isinstance(func, Step):
            raise TypeError("Callback is already a Step.")
        if not isinstance(handler, UpdateHandler):
            raise TypeError("handler param must be type of UpdateHandler.")

        handler.set_callback(func)
        sp = Step(func, handler, timeout, **kwargs)
        return sp

    return wrapper
