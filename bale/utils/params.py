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
from typing import Any, Tuple, get_type_hints
from inspect import signature as _signature, Parameter
from .types import F

def _tuple_to_str(tup: Tuple[Any, ...]) -> str:
    return ", ".join(
        item.__name__ for item in tup
    )

def check_annotation(item: Tuple[str, Any], annotation: Any) -> None:
    param_name, value = item
    expected_class_type = annotation

    if hasattr(annotation, '__args__'):  # Optional[Test], Union[int, float] and all typing objects has __attr__ variable
        expected_class_type = annotation.__args__

        # must be check all of that
        if isinstance(value, list) and getattr(annotation, '__origin__', None) is list:
            for i in value:
                check_annotation((param_name, i), expected_class_type)
            return

    if not Parameter.empty in (annotation, expected_class_type) and not isinstance(value, expected_class_type):
        raise TypeError(
            '{param_name} param must be type of {expected_class_type}'.format(
                param_name=param_name,
                expected_class_type=_tuple_to_str(expected_class_type)
            )
        )

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
        except TypeError: # a parameter is missing. so, to obtain a better error, we execute it.
            return func(*args, **kwargs)
        else:
            bound_obj.apply_defaults()

        for param in signature.parameters.keys():
            if not param in type_hints:
                continue

            check_annotation(
                (
                    param,
                    bound_obj.arguments.get(param)
                ),
                type_hints[param]
            )

        return await func(*args, **kwargs)

    return wrapper
