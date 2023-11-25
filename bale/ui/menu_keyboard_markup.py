from __future__ import annotations
from typing import Optional, Dict, Self
from . import BaseReplyMarkup, MenuKeyboardButton, ReplyMarkupItem

class MenuKeyboardMarkup(BaseReplyMarkup):
    def __init__(self):
        super().__init__()

    def add(self, keyboard_button: MenuKeyboardButton, row: Optional[int] = None) -> Self:
        """Add a Menu Keyboard button to keyboards.

        .. warning::
            Your numbers in the "row" param must be natural and greater than 0.

        Parameters
        ----------
            keyboard_button: :class:`bale.MenuKeyboardButton`
                The menu keyboard button.
            row: Optional[:class:`int`]
                The row where you want the button to be placed.
        """
        if not isinstance(keyboard_button, MenuKeyboardButton):
            raise TypeError(
                "keyboard_button param must be type of KeyboardButton"
            )

        super()._add(keyboard_button, row)
        return self

    def remove(self, item: "ReplyMarkupItem") -> Self:
        """Remove a Reply Markup item from keyboards.

        Parameters
        ----------
            item: :class:`bale.ReplyMarkupItem`
                The reply markup item.
        """
        super()._remove(item)
        return self

    def remove_row(self, row: int) -> Self:
        """Remove a row along with the menu keyboards located in that row.

        Parameters
        ----------
            row: :class:`int`
                The row.
        """
        super()._remove_row(row)
        return self

    def to_dict(self) -> Dict:
        components = []
        payload = {
            "keyboard": components
        }
        for group in super()._to_components():
            components.append([keyboard_button.to_dict() for keyboard_button in group])

        return payload