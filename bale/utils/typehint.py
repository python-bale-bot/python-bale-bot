# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
import functools
from typing import Any, Tuple, get_type_hints, TypeVar, Union
from inspect import signature as _signature, Parameter
from .types import F

A = TypeVar('A')


def _tuple_to_str(tup: Tuple[Any, ...]) -> str:
    return ", ".join(
        item.__name__ for item in tup
    )


def parse_annotation(annotation: A) -> Union[A, Tuple[Any, ...]]:
    if hasattr(annotation,
               '__args__'):  # Optional[Test], Union[int, float] and all typing objects has __attr__ variable
        annotation = annotation.__args__
    return annotation


def check_annotation(value: Any, annotation: Any) -> bool:  # value=[1, 2, 3], annotation=List[int]
    expected_class_type = parse_annotation(annotation)

    if getattr(annotation, '__origin__', None) is list and isinstance(value, list):
        for i in value:
            if not check_annotation(i, expected_class_type):
                return False
    else:
        if Parameter.empty not in (annotation, expected_class_type) and not isinstance(value, annotation):
            return False
    return True


def arguments_shield(func: F) -> F:
    """
    Decorator functions work like this:
    .. code:: python

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
        type_hints = get_type_hints(func)
        try:
            bound_obj = signature.bind(*args, **kwargs)
        except TypeError:  # a parameter is missing. so, to obtain a better error, we execute it.
            return func(*args, **kwargs)
        else:
            bound_obj.apply_defaults()

        for p_name in signature.parameters.keys():
            type_hint = type_hints.get(p_name)
            if not type_hint:
                continue

            check = check_annotation(bound_obj.arguments.get(p_name), type_hint)
            if not check:
                raise TypeError(
                    f'{p_name} param must be type of {type_hint}'
                )

        return await func(*args, **kwargs)

    return wrapper
