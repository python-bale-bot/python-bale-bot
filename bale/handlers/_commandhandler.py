# An API wrapper for Bale written in Python
# Copyright (c) 2022-2026
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

import inspect
import logging
import typing
from collections.abc import Callable, Coroutine
from contextlib import suppress
from re import match as re_match
from types import UnionType as types_UnionType
from typing import TYPE_CHECKING, Any, cast

from bale.checks import Check

from .._exceptions import BadArgument, MissingRequiredArgument, UserInputError
from ._converter import ChatConverter, Converter, UserConverter
from ._updatehandler import UpdateHandler

if TYPE_CHECKING:
    from bale.context import Context

Prefix = str | list[str]
PrefixCallable = Callable[["Context"], Coroutine[Any, Any, bool]]
PrefixType = PrefixCallable | Prefix

_log = logging.getLogger(__name__)


class CommandHandler(UpdateHandler):
    """This object shows an Additional Message Handler.
    In this handler, only updates that show a sent message and whose message text matches the predefined command and its arguments, and also meet the conditions set in :paramref:`check`, are covered.

    Arguments:
        command:
            The list of commands that the handler is required to cover. It can be a string or a list of strings.
        prefix:
            The command prefix.
        check:
            The check function for this handler.

            Hint:

                Called in :meth:`check_new_update`, when new update confirm.
                This checker indicates whether the Update should be covered by the handler or not.

    Note:
        All additional keyword arguments passed to this handler will be forwarded to the base :class:`~bale.handlers.UpdateHandler`
        via ``**kwargs``.

    .. admonition:: Input parameters for the wrapper function
        :class: seealso

        **message**: :class:`~bale.Message`
            The only parameter for this handler is the received message object.



        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale.handlers import CommandHandler

                @client.handle(CommandHandler(['start', 'help']))
                async def command_handler(message: Message):
                    return await message.reply('')

    See Also:
        :any:`bale.handlers.cooldown`

    .. versionadded:: 3.0
    """

    __slots__ = ("commands", "check", "_prefix", "_signature")

    def __init__(
        self,
        command: str | list[str],
        prefix: PrefixType = "/",
        check: Check | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        commands = [command] if not isinstance(command, list) else command

        for comm in commands:
            if not re_match(r"^[\da-z_]{1,32}$", comm):
                raise ValueError(f"command `{comm}` must be has valid characters")

        if check and not isinstance(check, Check):
            raise TypeError("check param must be type of Check")

        self.commands = [comm.lower() for comm in commands]
        self.check: Check | None = check
        self._prefix = prefix
        self._signature: inspect.Signature | None = None

    def process_string_command(self, text: str) -> list[str]:
        """When a command is sent to the command handler for processing, the responsibility of analyzing the command string lies with this method. This method extracts all the parameters present in the command according to the following algorithm:

        .. code-block:: text

            set `text` equal to the command string.
            set `start` equal to 0.
            set `flag` equal to false.
            set `words` equal to an empty list of strings.
            for each character `cw` in `text` and its position `current`, do the following:
                if `cw` is equal to the double quote character (`"`), do:
                    if `flag` is true, then do:
                        add the substring of `text` from index `start` to `current` to `words`.
                        set `start` equal to `current`.
                    toggle the value of `flag`.
                    increment `start` by 1.
                if `cw` is a space character or we are at the end of `text`, and `flag` is false, do:
                    if `current` is not equal to `start`, then do:
                        add the substring of `text` from index `start` to `current` to `words`.
                        set `start` equal to `current`.
                    increment `start` by 1.


        Thus, at the end, the value of ``words`` will represent the arguments passed in the command sequentially.

        Arguments:
            text
                The text of the message.


        Returns:
             The list of arguments passed in the command.
        """
        start = 0
        flag = False
        words: list[str] = []
        # command "first argument"     "second argument"
        # command first "second argument"
        for current, cw in enumerate(text):
            if cw == '"':
                if flag:
                    words.append(text[start:current])
                    start = current

                flag = not flag
                start += 1
            elif (cw.isspace() or current + 1 == len(text)) and not flag:
                end = (
                    current + 1
                    if current + 1 == len(text) and not cw.isspace()
                    else current
                )
                if end != start:
                    words.append(text[start:end])

                start = current + 1

        return words

    async def get_prefix(self, context: "Context") -> Prefix:
        prefix = self._prefix

        if callable(prefix):
            prefix = prefix(context)
            if inspect.iscoroutine(prefix):
                prefix = await prefix

        if not isinstance(prefix, (str, list)):
            raise TypeError(
                f"prefix param must be a string, list of strings or a callable that return those, not {prefix.__class__.__name__}."
            )

        return prefix

    async def check_prefix(self, context: "Context") -> str | None:
        message_text: str = context.ensure_effective_message().text or ""
        prefixes = await self.get_prefix(context)
        if isinstance(prefixes, list):
            for prefix in prefixes:
                if message_text.startswith(prefix):
                    return prefix
        elif isinstance(prefixes, str) and message_text.startswith(prefixes):
            return prefixes

        return None

    async def match_parameter(
        self, context: "Context", name: str, raw: str, expected_type
    ) -> Any:
        origin = typing.get_origin(expected_type)
        args = typing.get_args(expected_type)

        if origin is None:
            if expected_type in (int, float):
                with suppress(Exception):
                    return expected_type(raw)
            elif expected_type is str:
                return raw
            elif expected_type is bool:
                bool_mapping = {
                    "true": True,
                    "false": False,
                    "1": True,
                    "0": False,
                    "y": True,
                    "n": False,
                }
                if raw in bool_mapping:
                    return bool_mapping[raw]
            elif inspect.isclass(expected_type) and issubclass(
                expected_type, Converter
            ):
                if result := await expected_type()(context, raw):
                    return result
            elif isinstance(expected_type, Converter):
                if result := await expected_type(context, raw):
                    return result
            else:
                from bale import Chat, User

                convert_mapping = {User: UserConverter, Chat: ChatConverter}
                if expected_type in convert_mapping:
                    expected_type: typing.Type[User] | typing.Type[Chat]
                    if result := await convert_mapping[expected_type]()(context, raw):
                        return result
        else:
            if origin is typing.Literal:
                for lit in args:
                    if raw == lit:
                        return raw
            if origin in (types_UnionType, typing.Union):
                for annotation in args:
                    with suppress(Exception):
                        return self.match_parameter(context, name, raw, annotation)

        raise BadArgument(name, raw, expected_type)

    async def _parse_arguments(self, context: "Context", text: str) -> list[Any]:
        string_args = self.process_string_command(text)
        sig = cast(inspect.Signature, self._signature)
        params = iter(sig.parameters.items())
        skip_count = (self._self is not None) + 1

        [next(params) for _ in range(skip_count)]

        arguments = []
        for name, param_obj in params:
            has_default = param_obj.default is not sig.empty
            annotation = param_obj.annotation

            if not string_args:
                if not has_default:
                    raise MissingRequiredArgument(name)
                arguments.append(param_obj.default)
                continue

            raw = string_args.pop(0)

            try:
                converted = await self.match_parameter(context, name, raw, annotation)
            except Exception as exc:
                if not isinstance(exc, UserInputError):
                    raise BadArgument(name, raw, annotation) from exc
                raise exc

            arguments.append(converted)

        return arguments

    def set_callback(self, callback: Callable[[Any], Coroutine[Any, Any, Any]]):
        super().set_callback(callback)
        sig = inspect.Signature.from_callable(callback)
        parameters = sig.parameters
        if len(parameters) == 0:
            raise RuntimeError(
                f'The function "{callback.__name__}" has no parameters for {self} handler. CommandHandler requires a parameter as the first argument.'
            )

        for name, param in parameters.items():
            kind = param.kind
            if kind in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
                raise TypeError(
                    f"Can't set callback for {self} because "
                    f"The function '{callback.__name__}' has a {kind} parameter '{name}'. "
                    "This is not supported."
                )

        self._signature = sig

    async def check_new_update(self, context: "Context"):
        update = context.update
        message = update.message
        text = cast(
            str | None, message and message.text
        )  # None, if update doesn't has any message

        if text and (prefix := await self.check_prefix(context)):
            command, _, query = text[len(prefix) :].partition(" ")

            if (command in self.commands + []) and (
                not self.check or await self.check.check_update(context)
            ):
                context.handler = self
                return context, query

        return None

    async def handle_update(self, context: "Context", *args):
        if self.callback and len(args) >= 2:
            query = args[1] if args else ""
            try:
                parsed_arguments = await self._parse_arguments(context, query)
                context.args = parsed_arguments
                return await self._run_callback(
                    context, context, *parsed_arguments
                )  # pylint: disable=not-callable
            except Exception as exc:  # pylint: disable=broad-exception-caught
                return await self._on_error_wrapper(context, exc)

        return None
