from __future__ import annotations
from typing import List, Tuple
from itertools import groupby
from . import InlineKeyboard, MenuKeyboard

class Components:
    """This object shows a Component.

    .. admonition:: Examples
        :any:`Components Bot <examples.inline_markup>`
    """
    __slots__ = (
        "_menu_keyboards",
        "_inline_keyboards"
    )

    def __init__(self):
        self._menu_keyboards: List[Tuple["MenuKeyboard", int]] = []
        self._inline_keyboards: List[Tuple["InlineKeyboard", int]] = []

    @property
    def menu_keyboards(self) -> List["MenuKeyboard"]:
        """List[:class:`bale.MenuKeyboard`]: Represents the MenuKeyboards list."""
        return [item[0] for item in self._menu_keyboards]

    @property
    def inline_keyboards(self) -> List["InlineKeyboard"]:
        """List[:class:`bale.InlineKeyboard`]: Represents the InlineKeyboards list."""
        return [item[0] for item in self._inline_keyboards]

    def add_menu_keyboard(self, menu_keyboard: "MenuKeyboard", row: int = 1):
        """Use this method to add MenuKeyboard component.

        Parameters
        ----------
            menu_keyboard: :class:`bale.MenuKeyboard`
                The Component you want to add
            row: :class:`int`
                The Component row number
        """
        if not isinstance(menu_keyboard, MenuKeyboard):
            raise TypeError("menu_keyboard param must be type of MenuKeyboard")

        if not isinstance(row, int):
            raise TypeError("row param must be type of int")

        self._menu_keyboards.append((menu_keyboard, row))

    def remove_menu_keyboard(self, menu_keyboard: "MenuKeyboard", row: int = 1):
        """Use this method to remove MenuKeyboard component.

        Parameters
        ----------
            menu_keyboard: :class:`bale.MenuKeyboard`
                The Component you want to remove
            row: :class:`int`
                The Component row number
        """
        if not isinstance(menu_keyboard, MenuKeyboard):
            raise TypeError("menu_keyboard param must be type of MenuKeyboard")

        if not isinstance(row, int):
            raise TypeError("row param must be type of int")

        self._menu_keyboards.remove((menu_keyboard, row))

    def add_inline_keyboard(self, inline_keyboard: "InlineKeyboard", row: int = 1):
        """Use this method to add InlineKeyboard component.

        Parameters
        ----------
            inline_keyboard: :class:`bale.InlineKeyboard`
                The Component you want to add
            row: :class:`int`
                The Component row number
        """
        if not isinstance(inline_keyboard, InlineKeyboard):
            raise TypeError("inline_keyboard param must be type of InlineKeyboard")

        if not isinstance(row, int):
            raise TypeError("row param must be type of int")

        self._inline_keyboards.append((inline_keyboard, row))

    def remove_inline_keyboard(self, inline_keyboard: "InlineKeyboard", row: int = 1):
        """Use this method to remove InlineKeyboard component.

        Parameters
        ----------
            inline_keyboard: :class:`bale.InlineKeyboard`
                The Component you want to remove
            row: :class:`int`
                The Component row number
        """
        if not isinstance(inline_keyboard, InlineKeyboard):
            raise TypeError("inline_keyboard param must be type of InlineKeyboard")

        if not isinstance(row, int):
            raise TypeError("row param must be type of int")

        self._inline_keyboards.remove((inline_keyboard, row))

    def to_dict(self):
        is_used_menu_keyboard = bool(self._menu_keyboards)
        is_used_inline_keyboard = bool(self._inline_keyboards)

        if is_used_menu_keyboard and is_used_inline_keyboard:
            raise TypeError("you can't use menu keyboards and inline keyboards params together.")

        if not (is_used_menu_keyboard or is_used_inline_keyboard):
            raise TypeError("you must be use menu keyboards or inline keyboards param.")

        correct_children = self._menu_keyboards if is_used_menu_keyboard else self._inline_keyboards
        correct_children_name = "keyboard" if is_used_menu_keyboard else "inline_keyboard"
        def key(i: Tuple["InlineKeyboard" | "MenuKeyboard", int]):
            return i[1] or 1

        sorted_components = sorted(correct_children, key=key)
        components = []
        payload = {correct_children_name: components}

        for _, group in groupby(sorted_components, key=key):
            _components = []
            for item in group:
                component = item[0]
                _components.append(component.to_dict())

            components.append(_components)

        return payload