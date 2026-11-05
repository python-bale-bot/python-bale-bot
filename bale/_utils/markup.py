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

from typing import TYPE_CHECKING, Type, TypeVar

if TYPE_CHECKING:
    from bale import BaleObject

__all__ = ("parse_input",)

ButtonT = TypeVar("ButtonT", bound="BaleObject")


def parse_input(
    raw: str | tuple | ButtonT | list[str | ButtonT | list[str | ButtonT]] | None,
    button_class: Type[ButtonT],
) -> list[list[ButtonT]]:
    base_exc_message = (
        f"raw must be a string, {button_class.__name__}, or a nested list of those. "
    )

    if not raw:
        return [[]]

    if isinstance(raw, str):
        raw = [button_class(raw)]
    if isinstance(raw, tuple):
        raw = [button_class(*raw)]
    if isinstance(raw, button_class):
        raw = [raw]

    if isinstance(raw, list):
        res: list[list[ButtonT]] = []

        for i, keyboards in enumerate(raw):
            if isinstance(keyboards, str):
                keyboards = button_class(keyboards)

            if isinstance(keyboards, button_class):
                keyboards = [keyboards]

            if isinstance(keyboards, list):
                for j, keyboard in enumerate(keyboards):
                    if isinstance(keyboard, str):
                        keyboard = button_class(keyboard)

                    if not isinstance(keyboard, button_class):
                        raise TypeError(
                            base_exc_message
                            + f"not a list contains another list that contains {keyboard.__class__.__name__} at {i + 1}:{j + 1}"
                        )

                    keyboards[j] = keyboard

                res.append(keyboards)
                continue

            raise TypeError(
                base_exc_message
                + f"not a list contains {keyboards.__class__.__name__} at {i + 1}"
            )

        return res

    raise TypeError(base_exc_message + f"not a {raw.__class__.__name__}")
