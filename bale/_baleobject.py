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

import inspect
import logging
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Type, TypeVar

from ._utils.object import json
from ._utils.typehint import PayloadType

if TYPE_CHECKING:
    from bale import Bot


_log = logging.getLogger(__name__)
BaleObj = TypeVar("BaleObj")
PayloadT = TypeVar("PayloadT")

__all__ = ("BaleObject",)


class BaleObject:
    """
    A class that is used for all models in Bale. By inheriting from this class, models can convert a dictionary of data into a class instance, and also convert the class instance into a dictionary or JSON.

    Note:
        * If the model is locked using the :meth:`_lock` function, it will not be possible to set or delete its attributes.

        * If an ``_id`` is set for the model, it will be used in comparisons (equality or inequality).

    .. versionadded:: 2.5.0
    """

    __slots__ = (
        "_id",
        "_locked",
        "_additional_data",
        "__bot",
    )

    def __init__(self) -> None:
        self._id: Any = None
        self._locked: bool = False
        self._additional_data: dict[str, Any] = {}
        self.__bot: "Bot | None" = None

    @property
    def bot(self) -> "Bot | None":
        """:class:`~bale.Bot`: configured bot object for this object."""
        return self.__bot

    @property
    def additional_data(self) -> dict[str, Any]:
        """dict[str, Any]: Additional information granted to the object."""
        return self._additional_data

    @property
    def locked(self) -> bool:
        """:obj:`bool`: Indicates whether the model is locked."""
        return self._locked

    def _lock(self) -> None:
        self._locked = True

    def _unlock(self) -> None:
        self._locked = False

    def get_bot(self) -> "Bot":
        """Use this method to obtain a bot object that is configured for the model. This means that if no bot object is configured, the function will encounter an error.

        Raises
        ------
            RuntimeError
                A bot object is not configured for this model.

        Returns:
            The configured bot object fot this model.

        :meta public:
        """
        if not self.__bot:
            raise RuntimeError(
                f"Bot object is not set for `{self.__class__.__name__}`!"
            )

        return self.__bot

    def set_bot(self, bot: "Bot") -> None:
        self.__bot = bot

    def __setattr__(self, key: str, value: Any) -> None:
        """
        :meta private:
        """
        if key.startswith("_") or not getattr(self, "_locked", True):
            super().__setattr__(key, value)
            return

        raise AttributeError(
            f"You can't set `{key}` attribute to `{self.__class__.__name__}`!"
        )

    def __delattr__(self, item: str) -> None:
        """
        :meta private:
        """
        if item.startswith("_") or not getattr(self, "_locked", True):
            super().__delattr__(item)
            return

        raise AttributeError(
            f"You can't delete `{item}` attribute from `{self.__class__.__name__}`!"
        )

    def __eq__(self, other: object) -> bool:
        """
        :meta private:
        """
        if isinstance(other, self.__class__):
            return self._id == other._id

        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        """
        :meta private:
        """
        return not self.__eq__(other)

    def __repr__(self) -> str:
        additional_data_repr = ", ".join(
            [f"{key}={value!r}" for key, value in self.additional_data.items()]
        )
        joined_attrs = ", ".join(
            [
                f"{key}={value!r}"
                for key, value in self._get_public_attrs().items()
                if value
            ]
        )
        extra = ""
        if joined_attrs:
            extra += f" {joined_attrs}"
        if additional_data_repr:
            extra += f" {additional_data_repr}"

        return f"<{self.__class__.__name__}{extra}>"

    def __getitem__(self, key: Any):
        # try additional data
        if key in self._additional_data:
            value = self.additional_data[key]
        # try attribute
        else:
            value = getattr(self, key, None)

        return value

    def __delitem__(self, key: Any) -> None:
        if key in self.additional_data:
            del self.additional_data[key]
        else:
            self.__delattr__(key)

    @classmethod
    def _get_signature_parameters(cls) -> MappingProxyType[str, inspect.Parameter]:
        return inspect.signature(cls.__init__).parameters

    def _get_public_attrs(self, *, to_dict: bool = False) -> dict[str, Any]:
        def try_to_dict(key: str):
            val = getattr(self, key, None)
            if to_dict:
                if hasattr(val, "to_dict") and callable(val.to_dict):
                    return val.to_dict()
                if isinstance(val, list):
                    return [
                        (
                            item.to_dict()
                            if hasattr(item, "to_dict") and callable(item.to_dict)
                            else (
                                item.copy()
                                if hasattr(item, "copy") and callable(item.copy)
                                else item
                            )
                        )
                        for item in val
                    ]
                if hasattr(val, "copy") and callable(val.copy):
                    return val.copy()

            return val

        slots: set[str] = set()
        for base in self.__class__.__mro__:  # noqa
            base_slots = getattr(base, "__slots__", ())
            # "The __slots__ declaration can take a sequence of strings, an iterable of strings, or a single string with the name of one attribute."
            if isinstance(base_slots, str):
                slots.add(base_slots)
                continue
            slots.update(base_slots)

        attributes: dict[str, Any] = {
            key: try_to_dict(key) for key in slots if key[0] != "_"
        }

        return attributes

    def to_json(self) -> str:
        """
        Convert the object to a JSON-formatted string.

        Returns:
            A JSON string representation of the object.
        """
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        """Places all the set public attributes into a dictionary and returns it.


        Important:
            If any attribute values have a :meth:`to_dict` function, that function will be called.
        """
        data = self._get_public_attrs(to_dict=True)

        if "from_user" in data:  # Replace form_user to user
            data["user"] = data.pop("from_user")
        return data

    @classmethod
    def from_dict(
        cls: Type["BaleObj"],
        data: PayloadT | None = None,
        bot: "Bot | None" = None,
    ) -> "BaleObj | None":
        """
        Converts a dictionary of public attributes into an instance of that object.

        Arguments:
            data:
                The payload.
            bot:
                The bot object for the model.

        Returns:
            an instance of :paramref:`cls`
        """
        # Unfortunately, mypy cannot infer that data is definitely not None in this point.
        if not (data and isinstance(data, dict)):
            return None

        parameters = cls._get_signature_parameters()
        existing_kwargs: dict[str, Any] = {}
        for key in parameters:
            if key == "self":
                continue
            if key not in data and (parameters[key].default is inspect.Parameter.empty):
                _log.warning(
                    "The %s argument is required in the %s class, but this value was not "
                    "found in the given data.",
                    key,
                    cls.__name__,
                )

            existing_kwargs[key] = data.pop(key, None)

        additional_data: dict[str, Any] = data

        obj = cls(**existing_kwargs)  # noqa
        obj._additional_data = additional_data
        if bot:
            obj.set_bot(bot)

        return obj

    @classmethod
    def from_list(
        cls: Type["BaleObj"],
        payloads_list: list[PayloadT] | None = None,
        bot: "Bot | None" = None,
    ) -> tuple["BaleObj | None"] | None:
        """
        This function works similarly to :meth:`from_dict`, but with the difference that it receives a tuple of dictionaries. One of the uses of this function can be seen in :meth:`~bale.Bot.get_chat_members`.

        Arguments:
            payloads_list:
                The list of payloads.
            bot:
                The bot object for the model.

        Returns:
            a tuple of instances of :paramref:`cls`.

        .. versionadded:: 3.0
        """
        if not payloads_list or not isinstance(payloads_list, list):
            return None

        objects = tuple(cls.from_dict(payload, bot) for payload in payloads_list)
        return objects

    @staticmethod
    def parse_data(data: PayloadType) -> PayloadType:
        """Validate and return a shallow copy of the given data dictionary.

        Arguments:
            data: The input data to parse, expected to be a dictionary.

        Returns:
            A shallow copy of the input dictionary if valid; otherwise, None if the input is None or not a dictionary.
        """
        if not data or not isinstance(data, dict):
            return None

        return data.copy()
