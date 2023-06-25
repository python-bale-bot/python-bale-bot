from typing import List, Tuple
from itertools import groupby
from . import InlineKeyboard, MenuKeyboard

class Components:
    __slots__ = (
        "_menu_keyboards",
        "_inline_keyboards"
    )

    def __int__(self):
        self._menu_keyboards: List[Tuple["MenuKeyboard", int]] = []
        self._inline_keyboards: List[Tuple["InlineKeyboard", int]] = []

    def add_menu_keyboard(self, menu_keyboard: "MenuKeyboard", row: int = None):
        self._menu_keyboards.append((menu_keyboard, row))

    def remove_menu_keyboard(self, menu_keyboard: "MenuKeyboard", row: int = None):
        self._menu_keyboards.remove((menu_keyboard, row))

    def add_inline_keyboard(self, inline_keyboard: "InlineKeyboard", row: int = None):
        self._inline_keyboards.append((inline_keyboard, row))

    def remove_inline_keyboard(self, inline_keyboard: "InlineKeyboard", row: int = None):
        self._inline_keyboards.remove((inline_keyboard, row))

    def to_dict(self):
        is_used_menu_keyboard = bool(self._menu_keyboards)
        is_used_inline_keyboard = bool(self._inline_keyboards)

        if is_used_menu_keyboard and is_used_inline_keyboard:
            raise TypeError("you can't use menu keyboards and inline keyboards params together.")

        if not (is_used_menu_keyboard and is_used_inline_keyboard):
            raise TypeError("you must be use menu keyboards or inline keyboards param.")

        correct_children = self._menu_keyboards if bool(self._menu_keyboards) else self._inline_keyboards
        correct_children_name = "keyboard" if bool(self._menu_keyboards) else "inline_keyboard"
        def key(item: Tuple["InlineKeyboard" | "MenuKeyboard", int]):
            return item[1] or 1

        sorted_components = sorted(correct_children, key=key)
        payload = {correct_children_name: {}}

        for _, group in groupby(sorted_components, key=key):
            _components = []
            for component in group:
                _components.append(component.to_dict())

            payload[correct_children_name].append(_components)

        return payload