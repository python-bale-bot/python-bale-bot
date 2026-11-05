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
import asyncio
import inspect
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bale.storage import BaseStorage

__all__ = (
    "validate_timeout",
    "validate_storage",
    "check_subclass",
    "iscoroutinefunction",
)


def validate_timeout(timeout: Any) -> float | None:
    if timeout is None:
        return None

    if isinstance(timeout, int):
        timeout = float(timeout)

    if timeout <= 0:
        raise ValueError(f"timeout must be greater than 0, got {timeout!r}.")

    if not isinstance(timeout, float):
        raise TypeError(
            f"timeout must be int, float, or None, " f"not {type(timeout).__name__}."
        )

    return timeout


def validate_storage(storage: "BaseStorage") -> None:
    from bale.storage import BaseStorage

    if not isinstance(storage, BaseStorage):
        raise TypeError(
            f"Expected an instance of BaseStorage, got {type(storage).__name__} instead."
        )


def check_subclass(cls: Any, bases: type) -> None:
    if not isinstance(cls, type) or not issubclass(cls, bases):
        bases_name = bases.__name__
        raise TypeError(
            f"The {cls.__name__} must be {bases_name} or a subclass of {bases_name}."
        )


# Thanks @Jackenmen
# `inspect.iscoroutinefunction()` only became equivalent to (now deprecated) `inspect.iscoroutinefunction()` in Python 3.12
# https://github.com/python/cpython/issues/122858#issuecomment-2466239748
if sys.version_info >= (3, 12):
    iscoroutinefunction = inspect.iscoroutinefunction
else:
    iscoroutinefunction = asyncio.iscoroutinefunction
