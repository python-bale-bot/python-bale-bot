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
from collections.abc import Callable
from typing import Any

__all__ = ("unwrap_function",)


def unwrap_function(function: Callable[..., Any], /) -> Callable[..., Any]:
    partial = functools.partial
    while True:
        if hasattr(function, "__wrapped__"):
            function = function.__wrapped__
        elif isinstance(function, partial):
            function = function.func
        else:
            return function
