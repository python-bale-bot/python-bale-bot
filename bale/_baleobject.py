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
from typing import TYPE_CHECKING, Any, Type, List, Dict, TypeVar, Optional
import logging
import inspect
from json import dumps
if TYPE_CHECKING:
    from bale import Bot

_log = logging.getLogger(__name__)
Bale_obj_instance = TypeVar("Bale_obj_instance", bound="BaleObject", covariant=True)

__all__ = (
    "BaleObject",
)

class BaleObject:
    __slots__ = (
        "__bot",
        "_id",
        "_locked"
    )
    def __init__(self) -> None:
        self.__bot: Optional["Bot"] = None
        self._id = None
        self._locked: bool = False

    @property
    def bot(self) -> Optional["Bot"]:
        return self.__bot

    @bot.setter
    def bot(self, value) -> None:
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

    def set_bot(self, bot: "Bot") -> None:
        self.__bot = bot

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith('_') or not getattr(self, "_locked", True):
            super().__setattr__(key, value)
            return

        raise AttributeError(
            "You can't set `%s` attribute to `%s`!", key, self.__class__.__name__
        )

    def __delattr__(self, item: str) -> None:
        if item.startswith('_') or not getattr(self, "_locked", True):
            super().__delattr__(item)
            return

        raise AttributeError(
            "You can't delete `%s` attribute from `%s`!", item, self.__class__.__name__
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
                f"{k}={repr(v)}"
                for k, v in attrs.items() if not k.startswith("_") and v
            ])
        )

    @classmethod
    def _get_signature_parameters(cls):
        return inspect.signature(cls).parameters

    def _get_attrs(self, *, to_dict: bool) -> Dict[str, Any]:
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
        data = {
            key: value
            for key, value in self._get_attrs(to_dict=True).items()
            if not key.startswith('_')
        }

        if "from_user" in data:
            data["from"] = data.pop("from_user")
        return data

    @classmethod
    def _from_dict(cls: Type[Bale_obj_instance], data: Optional[Dict], bot: "Bot"
                   ) -> Optional[Bale_obj_instance]:
        if not data:
            return None

        def has_default(key: str) -> bool:
            param = parameters[key]
            return not param.default is param.empty

        def get_attr(key: str) -> Any:
            if not key in data and not has_default(key):
                _log.warning("The %s argument is required in the %s class, but this value was not found in the given data.", key, cls.__name__)

            return data.get(key)

        parameters = cls._get_signature_parameters()
        existing_kwargs = {
            key: get_attr(key) for key in parameters
        }
        obj: Bale_obj_instance = cls(**existing_kwargs)

        obj.set_bot(bot)
        return obj

    @classmethod
    def from_dict(cls: Type[Bale_obj_instance], data: Optional[Dict], bot: "Bot"
                   ) -> Optional[Bale_obj_instance]:
        return cls._from_dict(data=data, bot=bot)

    @classmethod
    def from_list(cls: Type[Bale_obj_instance], payloads_list: Optional[List[Dict]], bot: "Bot") -> Optional[List[Bale_obj_instance]]:
        if not payloads_list or not isinstance(payloads_list, list):
            return None

        objects = []
        for obj_payload in payloads_list:
            obj: Bale_obj_instance = cls._from_dict(data=obj_payload, bot=bot)
            objects.append(obj)

        return objects

    @staticmethod
    def parse_data(data: Optional[Dict]) -> Optional[Dict]:
        if not data:
            return None

        return data.copy()
