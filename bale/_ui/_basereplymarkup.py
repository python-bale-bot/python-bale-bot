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

from abc import ABC
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Type, TypeVar

from .._baleobject import BaleObject
from .._utils import markup as utils_markup

if TYPE_CHECKING:
    pass  # type: ignore

ButtonT = TypeVar("ButtonT", bound=BaleObject)
SelfT = TypeVar("SelfT", bound="ReplyMarkup")


class ReplyMarkup(ABC, BaleObject, Generic[ButtonT]):
    """Base class for representing a reply markup object in Bale Bot API.

    This abstract class defines a common interface for both inline and menu keyboards.
    Subclasses must implement the required methods to manage and render keyboard layouts.

    Note:
        - Only one of :paramref:`keyboards` or :paramref:`inline_keyboard` must be used.
        - Each keyboard is a list of rows, and each row is a list of buttons.
    """

    __slots__ = ("_keyboards", "_api_kwargs")

    _button_cls: type[ButtonT]
    _payload: ClassVar[str]

    def __init__(
        self,
        keyboards: (
            str | ButtonT | list[str | ButtonT | list[str | ButtonT]] | None
        ) = None,
        **api_kwargs,
    ):
        super().__init__()
        self._keyboards: list[list[ButtonT]] = self.__parse_keyboards(keyboards)
        self._api_kwargs = api_kwargs

    def __parse_keyboards(
        self,
        keyboards: (
            str | ButtonT | list[str | ButtonT | list[str | ButtonT]] | None
        ) = None,
    ) -> list[list[ButtonT]]:
        return utils_markup.parse_input(keyboards, self._button_cls)

    @property
    def keyboards(self) -> list[list[ButtonT]]:
        return [list(row) for row in self._keyboards]

    @keyboards.setter
    def keyboards(
        self, value: str | ButtonT | list[str | ButtonT | list[str | ButtonT]]
    ) -> None:
        self._keyboards = self.__parse_keyboards(value)

    def row(self: SelfT, *buttons: str | ButtonT) -> SelfT:
        if buttons:
            kb = self.keyboards
            kb.append(buttons)  # noqa

            self.keyboards = kb

        return self

    def add_row(
        self: SelfT, keyboards: list[str | ButtonT], index: int | None = None
    ) -> SelfT:
        """
        Adds a new row of buttons to the keyboard.

        Args:
            keyboards:
                A list of buttons to be added as a row.
            index:
                If provided, inserts the row at the specified index. Otherwise, appends it to the end.
        """
        kb = self.keyboards
        if index is None:
            kb.append(keyboards)  # noqa
        else:
            kb.insert(index, keyboards)  # noqa

        self.keyboards = kb
        return self

    def add_button(
        self: SelfT,
        keyboard: str | ButtonT,
        row: int | None = None,
        index: int | None = None,
    ) -> SelfT:
        """Adds a single button to an existing row in the keyboard.

        Args:
            keyboard:
                The button to be added.
            row:
                The row index where the button will be added. Defaults to the last row.
            index:
                If provided, inserts the button at the specified position in the row. Otherwise, appends it to the row.
        """
        kb = self.keyboards
        if not kb:
            kb.append([])

        target_row = row if row is not None else -1
        target_index = index if index is not None else len(kb[target_row])

        kb[target_row].insert(target_index, keyboard)  # noqa

        self.keyboards = kb
        return self

    def remove_row(self: SelfT, row: int) -> SelfT:
        """Removes an entire row of buttons from the keyboard.

        Args:
            row:
                The index of the row to be removed.

        Raises:
            IndexError:
                If the row index is out of range.
        """
        del self._keyboards[row]

        return self

    def remove_button(self: SelfT, row: int, index: int) -> SelfT:
        """Removes a button from a specific row and position.

        Args:
            row:
                The index of the row.
            index:
                The index of the button within the row.

        Raises:
            IndexError:
                If either the row or button index is out of range.
        """
        del self._keyboards[row][index]

        return self

    def __add__(self: SelfT, other: SelfT) -> SelfT:
        if not isinstance(other, self.__class__):
            return NotImplemented

        kb = self.keyboards
        kb.extend(other.keyboards)

        instance = self.__class__(kb)
        return instance

    def __iadd__(self: SelfT, other: SelfT) -> SelfT:
        if not isinstance(other, self.__class__):
            return NotImplemented

        self._keyboards.extend(other.keyboards)
        return self

    def _normalize_button(self, button: ButtonT | str):
        if isinstance(button, str):
            return self._button_cls(button)
        if not isinstance(button, self._button_cls):
            raise TypeError(
                f"button must be type of {self._button_cls.__name__} or str, not {type(button).__name__}"
            )

        return button

    @classmethod
    def from_dict(
        cls: Type[SelfT], data: dict[str, Any] | None = None, bot=None
    ) -> SelfT | None:
        """:meta private:"""
        data = BaleObject.parse_data(data)
        if not data:
            return None

        keyboards = data.pop(cls._payload, [])
        for index_r, row in enumerate(keyboards):
            for index_b, btn in enumerate(row):
                keyboards[index_r][index_b] = cls._button_cls.from_dict(btn, bot)

        return cls(keyboards)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            self._payload: [[btn.to_dict() for btn in row] for row in self._keyboards]
        }
        payload.update(self._api_kwargs)

        return payload
