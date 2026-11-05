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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TypeVar

__all__ = ("BaseStorage", "StorageConfig")

DictLike = dict[Any, Any]

Self = TypeVar("Self", bound="BaseStorage")


@dataclass
class StorageConfig:
    bot_data: bool
    chat_data: bool
    user_data: bool
    flow_data: bool


class BaseStorage(ABC):
    """An abstract base class responsible for handling data storage operations.

    It acts as an interface for retrieving, updating, and deleting data within the library.
    As such, all subclasses are required to implement the essential methods, such as :meth:`get_bot_data`.

    .. versionadded:: 3.0
    """

    __slots__ = ("_config",)

    def __init__(self, config: "StorageConfig") -> None:
        self._validate_config(config)
        self._config = config

    def _validate_config(self, config: "StorageConfig") -> None:
        checks = {
            "user_data": ("get_user_data", "set_user_data", "drop_user_data"),
            "chat_data": ("get_chat_data", "set_chat_data", "drop_chat_data"),
            "bot_data": ("get_bot_data", "set_bot_data", "drop_bot_data"),
            "flow_data": (
                "get_flow_data",
                "get_all_flow_data",
                "set_flow_data",
                "drop_flow_data",
            ),
        }

        for config_attr, methods in checks.items():
            if not getattr(config, config_attr, False):
                for method_name in methods:
                    current_method = getattr(self, method_name, None)
                    base_method = getattr(BaseStorage, method_name, None)
                    current_func = getattr(current_method, "__func__", current_method)

                    if current_func is not None and current_func is not base_method:
                        raise ValueError(
                            f"Storage implements '{method_name}', but '{config_attr}' is disabled in StorageConfig."
                        )

    @abstractmethod
    async def get_bot_data(self) -> DictLike:
        """This method is responsible for returning only the relevant with bot data.

        Subclasses are required to implement this method so that the returned object behaves like a dictionary—that is, it provides a dictionary-like interface similar to Python’s dictionaries, and is both readable and writable.

        Returns:
             The returned data must include general information and stored states maintained at the bot-wide level (not per user or per chat).
        """

    @abstractmethod
    async def get_chat_data(self, chat_id: int) -> DictLike:
        """This method is responsible for returning only the data related to the specific chat.

        Subclasses are required to implement this method so that the returned object behaves like a dictionary—that is, it provides a dictionary-like interface similar to Python’s dictionaries, and is both readable and writable.

        Arguments:
            chat_id:
                It is guaranteed that a number representing the unique identifier of the chat in question is provided.

        Returns:
             The returned data must include special information and stored states maintained at the chat level.
        """

    @abstractmethod
    async def get_user_data(self, user_id: int) -> DictLike:
        """This method is responsible for returning only the data related to the specific user.

        Subclasses are required to implement this method so that the returned object behaves like a dictionary—that is, it provides a dictionary-like interface similar to Python’s dictionaries, and is both readable and writable.

        Arguments:
            user_id:
                It is guaranteed that a number representing the unique identifier of the user in question is provided.


        Returns:
             The returned data must include special information and stored states maintained at the user level.
        """

    @abstractmethod
    async def get_flow_data(self, flow_key: str) -> DictLike:
        """This method is responsible for returning only the data related to a specific conversation flow.

        Subclasses are required to implement this method so that the returned object behaves like a dictionary—that is, it provides a dictionary-like interface similar to Python's dictionaries, and is both readable and writable.

        Arguments:
            flow_key:
                The unique identifier key representing the active conversation flow session.

        Returns:
            The returned data must include state data, step checkpoints, and payload maintained for the specified flow.
        """

    @abstractmethod
    async def get_all_flow_data(self) -> dict[str, DictLike]:
        """This method is responsible for retrieving all active conversation flow sessions and their associated data.

        Subclasses are required to implement this method to allow recovery or synchronization of all ongoing conversation flows across the system.

        Returns:
            A dictionary mapping each flow key to its corresponding dictionary-like session data.
        """

    @abstractmethod
    async def update_bot_data(self, data: Any) -> None:
        """This method is responsible for updating the data related to the bot.

        Subclasses are required to implement this method so that the changes are correctly applied and recorded in the storage system.

        Note:
            Error handling must be taken into consideration during the storage process.
            Additionally, since this method is called frequently, performance optimization and correctness of processing are **necessary**.

        Arguments:
            data:
                It is ensured that a dictionary-like object containing the data to be stored or modified is provided.
        """

    @abstractmethod
    async def update_chat_data(self, chat_id: int, data: DictLike) -> None:
        """This method is responsible for updating the data related to a specific chat.

        Subclasses are required to implement this method so that the changes are correctly applied and recorded in the storage system.

        Note:
            Error handling must be taken into consideration during the storage process.
            Additionally, since this method is called frequently, performance optimization and processing correctness are **necessary**.

        Arguments:
            chat_id:
                It is guaranteed that a number representing the unique identifier of the chat in question is provided.
            data:
                It is also guaranteed that a dictionary-like object containing the data to be stored or modified is provided.
        """

    @abstractmethod
    async def update_user_data(self, user_id: int, data: DictLike) -> None:
        """This method is responsible for updating the data related to a specific user.

        Subclasses are required to implement this method such that the changes are correctly applied and recorded in the storage system.

        Note:
            Error handling must be taken into consideration during the storage process.
            Additionally, since this method is called frequently, performance optimization and processing accuracy are **necessary**.

        Arguments:
            user_id:
                It is guaranteed that a number representing the unique identifier of the target user is provided.
            data:
                It is also guaranteed that a dictionary-like object containing the data to be stored or modified is provided.
        """

    @abstractmethod
    async def update_flow_data(self, flow_key: str, data: DictLike) -> None:
        """This method is responsible for updating the data related to a specific conversation flow.

        Subclasses are required to implement this method so that the changes are correctly applied and recorded in the storage system.

        Note:
            Error handling must be taken into consideration during the storage process.
            Additionally, since this method is called frequently during step transitions, performance optimization and processing accuracy are **necessary**.

        Arguments:
            flow_key:
                The unique identifier key representing the active conversation flow session.
            data:
                A dictionary-like object containing the flow state and data to be stored or modified.
        """

    @abstractmethod
    async def drop_chat_data(self, chat_id: int) -> None:
        """This method is responsible for removing all data associated with a specific chat from the storage system.

        Subclasses are required to implement this method in such a way that the changes are correctly applied and recorded in the storage system.

        Arguments:
            chat_id:
                It is guaranteed that the provided value is a number representing the unique identifier of the target chat.

        Note:
            If no data exists for the specified identifier, the method must not raise an error.
            Error handling must be considered during the storage process.
            Additionally, since this method may be called frequently, performance optimization and processing accuracy are **essential**.
        """

    @abstractmethod
    async def drop_user_data(self, user_id: int) -> None:
        """This method is responsible for removing all data associated with a specific user from the storage system.

        Subclasses are required to implement this method in such a way that the changes are correctly applied and recorded in the storage system.

        Arguments:
            user_id:
                It is guaranteed that the provided value is a number representing the unique identifier of the target user.

        Note:
            If no data exists for the specified identifier, the method must not raise an error.
            Error handling must be considered during the storage process.
            Additionally, since this method may be called frequently, performance optimization and processing accuracy are **essential**.
        """

    @abstractmethod
    async def drop_bot_data(self) -> None:
        """This method is responsible for removing all bot-wide data from the storage system.

        Subclasses are required to implement this method in such a way that the changes are correctly applied and recorded in the storage system.

        Note:
            If no bot data exists, the method must not raise an error.
            Error handling must be considered during the storage process, and performance optimization is **essential**.
        """

    @abstractmethod
    async def drop_flow_data(self, flow_key: str) -> None:
        """This method is responsible for removing all data associated with a specific conversation flow session from the storage system.

        Subclasses are required to implement this method in such a way that the changes are correctly applied and recorded in the storage system upon flow termination or timeout.

        Arguments:
            flow_key:
                The unique identifier key representing the conversation flow to be cleared.

        Note:
            If no data exists for the specified identifier, the method must not raise an error.
            Error handling must be considered during the storage process, and performance optimization is **essential**.
        """

    @abstractmethod
    async def initialize(self) -> None:
        """This method is invoked as a command to start the storage component.


        Note:
            Since update processing is guaranteed to begin before the completion of this method, any necessary prerequisites—particularly for database-based subclasses—must be fulfilled at this stage.

            This includes performing initialization steps and ensuring that the storage backend is ready for operation.
        """

    @abstractmethod
    async def close(self) -> None:
        """This method is invoked as a command to terminate the storage component.

        At this stage, finalization tasks such as closing active connections to databases and releasing system resources must be performed.


        Note:
            It is guaranteed that after this method is executed, none of the storage-related methods of this class will be called.
            Therefore, all subclasses are required to implement a safe and complete shutdown process within this method.
        """
