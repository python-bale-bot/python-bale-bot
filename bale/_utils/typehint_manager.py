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
import functools
import types
import typing
from collections.abc import Callable
from contextlib import suppress
from inspect import Parameter
from inspect import signature as _signature
from typing import Any, TypeVar, get_type_hints

A = TypeVar("A")
F = TypeVar("F", bound=Callable[..., Any])


def _tuple_to_str(tup: tuple[Any, ...]) -> str:
    return ", ".join(item.__name__ for item in tup)


def parse_annotation(annotation: A) -> A | tuple[Any, ...]:
    if hasattr(
        annotation, "__args__"
    ):  # str | None, int | float and most typing objects has __attr__ variable
        annotation = annotation.__args__
    return annotation


def check_annotation(
    value: Any, annotation: Any
) -> bool:  # value=[1, 2, 3], annotation=list[int]
    expected_class_type = parse_annotation(annotation)

    if getattr(annotation, "__origin__", None) is list and isinstance(value, list):
        for i in value:
            if not check_annotation(i, expected_class_type):
                return False
    else:
        if Parameter.empty not in (annotation, expected_class_type) and not isinstance(
            value, annotation
        ):
            return False

    return True


def get_resolved_hints(func):
    try:
        namespace: dict[Any, Any] = dict(func.__globals__)
    except AttributeError:
        namespace: dict[Any, Any] = {}

    with suppress(Exception):
        from bale import (InlineKeyboardMarkup, InputFile, ReplyKeyboardMarkup,
                          ReplyKeyboardRemove)

        namespace.setdefault("InlineKeyboardMarkup", InlineKeyboardMarkup)
        namespace.setdefault("ReplyKeyboardMarkup", ReplyKeyboardMarkup)
        namespace.setdefault("ReplyKeyboardRemove", ReplyKeyboardRemove)
        namespace.setdefault("InputFile", InputFile)

    return get_type_hints(func, globalns=namespace, localns=namespace)


def format_type_hint(hint: Any) -> str:
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)

    if origin is typing.Union or origin is types.UnionType:
        non_none_types: list[str] = [
            format_type_hint(i) for i in args if i is not type(None)
        ]
        is_optional = len(non_none_types) < len(args)

        formatted_types = (
            " | ".join(non_none_types) if len(non_none_types) > 1 else non_none_types[0]
        )
        return f"Optional[{formatted_types}]" if is_optional else formatted_types

    if origin is not None:
        origin_name: str = getattr(origin, "__name__", str(origin))
        if origin_name in ["list", "dict"] and len(origin_name) > 0:
            origin_name = origin_name[0].upper() + origin_name[1:]

        if args:
            rep = (
                ", ".join([format_type_hint(i) for i in args])
                if len(args) > 1
                else format_type_hint(args[0])
            )
            return f"{origin_name}[{rep}]"

    if isinstance(hint, type):
        return hint.__name__

    return str(hint).replace("typing.", "")


def arguments_shield(func: F) -> F:
    """
    Decorator functions work like this:
    .. code-block:: python

        def decorator(func):
            return func

        @decorator
        def func():
            pass

        # This is equivalent to:

        func = decorator(func)

    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        signature = _signature(func)
        type_hints = get_resolved_hints(func)
        try:
            bound_obj = signature.bind(*args, **kwargs)
        except (
            TypeError
        ):  # a parameter is missing. so, to obtain a better error, we execute it.
            return await func(*args, **kwargs)

        bound_obj.apply_defaults()

        for p_name in signature.parameters.keys():
            type_hint = type_hints.get(p_name)
            if not type_hint:
                continue

            actual_type = bound_obj.arguments.get(p_name)
            check = check_annotation(actual_type, type_hint)
            if not check:
                formatted_type_hint = format_type_hint(type_hint)
                raise TypeError(
                    f"Parameter {p_name} must be type of {formatted_type_hint}, got {type(actual_type).__name__}"
                )

        return await func(*args, **kwargs)

    return wrapper
