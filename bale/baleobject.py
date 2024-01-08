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
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Type, Set, Dict, TypeVar, Optional
import inspect
from json import dumps
if TYPE_CHECKING:
    from bale import Bot

Bale_obj = TypeVar("Bale_obj", bound="BaleObject", covariant=True)

__all__ = (
    "BaleObject",
)

class BaleObject:
    __slots__ = (
        "__bot",
        "_id",
        "_locked"
    )
    def __init__(self):
        self.__bot: Optional["Bot"] = None
        self._id = None
        self._locked: bool = False

    @property
    def bot(self) -> Optional["Bot"]:
        return self.__bot

    @bot.setter
    def bot(self, value):
        self.set_bot(value)

    def _lock(self) -> None:
        self._locked = True

    def _unlock(self) -> None:
        self._locked = False

    def get_bot(self) -> "Bot":
        if not self.__bot:
            raise RuntimeError(
                "Bot object is not set for `{}`!".format(self.__class__.__name__)
            )

        return self.__bot

    def set_bot(self, bot: "Bot"):
        self.__bot = bot

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith('_') or not getattr(self, "_locked", True):
            super().__setattr__(key, value)
            return

        raise AttributeError(
            "You can't set `{}` attribute to `{}`!".format(key, self.__class__.__name__)
        )

    def __delattr__(self, item: str) -> None:
        if item.startswith('_') or not getattr(self, "_locked", True):
            super().__delattr__(item)
            return

        raise AttributeError(
            "You can't delete `{}` attribute from `{}`!".format(item, self.__class__.__name__)
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._id == other._id
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        attrs = self._get_attrs(to_dict=False)
        return "<{} {}>".format(
            self.__class__.__name__,
            ", ".join([
                "{}={}".format(key, repr(value)) for key, value in attrs.items() if not key.startswith("_") and value
            ])
        )

    @classmethod
    def _get_signature_keys(cls) -> Set:
        return set(inspect.signature(cls).parameters.keys())

    def _get_attrs(self, *, to_dict: bool) -> Dict:
        attributes = {item: getattr(self, item, None) for cls in self.__class__.__mro__[:-1] for item in cls.__slots__}
        for key, value in attributes.items():
            if not to_dict:
                continue
            if hasattr(value, 'to_dict'):
                attributes[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                for index, item in enumerate(value):
                    if hasattr(value, 'to_dict'):
                        attributes[key][index] = item.to_dict()
        return attributes

    def to_json(self) -> str:
        return dumps(self.to_dict())

    def to_dict(self) -> Dict:
        data = {k: v for k, v in self._get_attrs(to_dict=True).items() if not k.startswith('_')}

        if "from_user" in data:
            data["from"] = data.pop("from_user")
        return data

    @classmethod
    def _from_dict(cls: Type[Bale_obj], data: Optional[Dict], bot: "Bot") -> Optional[Bale_obj]:
        if not data:
            return None

        existing_kwargs = {
                key: data.get(key) for key in cls._get_signature_keys()
            }
        obj: Bale_obj = cls(**existing_kwargs)

        obj.set_bot(bot)
        return obj

    @classmethod
    def from_dict(cls: Type[Bale_obj], data: Optional[Dict], bot: "Bot") -> Optional[Bale_obj]:
        return cls._from_dict(data=data, bot=bot)

    @staticmethod
    def parse_data(data: Optional[Dict]) -> Optional[Dict]:
        return None if not data else data.copy()