from __future__ import annotations
import requests
from bale import (Message, Update, User, Components, Chat, Price, ChatMember, BaleError, InvalidToken, ApiError, NetworkError, TimeOut)


class Bot:
    """This object represents a Bale Bot.

        Args:
            token (str): Bot Token.
            base_url (str): API service URL. Defaults to "https://tapi.bale.ai/".
            base_file_url (str): API service file URL. Defaults to "https://tapi.bale.ai/file".

        Raises:
            :class:`bale.Error`
    """
    __slots__ = (
        "_user",
        "token",
        "base_url",
        "base_file_url",
        "_requests"
    )

    def __init__(self, token: str, base_url: str = "https://tapi.bale.ai/",
                 base_file_url: str = "https://tapi.bale.ai/file"):
        self.token = token
        self.base_url = base_url
        self.base_file_url = base_file_url
        self._requests = requests
        self._user = self.check_token()
        if not self._user:
            raise InvalidToken(f"Token {token} is Invalid!")

    def check_token(self, timeout=(30, 10)) -> bool | BaleError:
        """Check the entered token.

        Args:
            timeout (tuple, optional): Defaults to (30, 10).
        Returns:
            bool: If it is "True" it is returned True, if it is "False" it is returned False.
        Raises:
            :class:`BaleError`
        """
        if not isinstance(timeout, (tuple, int)):
            return False
        result = self.req("get", "getme", timeout=timeout)
        result = result.json()
        if result.json()["ok"]:
            return result.json()["ok"]
        raise ApiError(
            str(result.get("error_code")) + result.get("description")
        )

    def get_bot(self, timeout=(30, 10)) -> (User | BaleError):
        """Get Bot.

        Args:
            timeout (tuple, optional): Defaults to (30, 10).

        Returns:
            :class:`Bale.User`: Bot User information.
        Raises:
            :class:`Bale.Error`
        """
        result = self.req("GET", "getme", timeout=timeout)
        result = result.json()
        if result.get("ok", False):
            return User.from_dict(data=result["result"], bot=self)
        else:
            raise ApiError(
                str(result.get("error_code")) + result.get("description")
            )

    @property
    def bot(self):
        """Get Bot User

        Returns:
            :class:`bale.User`
        """
        if self._user is None:
            self._user = self.get_bot()
        return self._user

    def req(self, method: str, type: str, data: dict = None, params: dict = None, timeout=(5, 10)) -> requests.Response:
        """

        Args:
            method:
            type:
            data:
            params:
            timeout:

        Returns:
            :class:`requests.Response`
        Raises:
            :class:`bale.Error`
        """
        method = method.upper()
        try:
            if method == "POST":
                return self._requests.post(self.base_url + ("" if self.base_url.endswith("/") else "/") + (
                    f"bot" f"{self.token}" "/" f"{type}"), json=data, params=params, timeout=timeout)
            elif method == "GET":
                return self._requests.get(self.base_url + ("" if self.base_url.endswith("/") else "/") + (
                    f"bot" f"{self.token}" "/" f"{type}"), params=params, timeout=timeout)
        except requests.Timeout:
            raise TimeOut()
        except requests.ConnectionError:
            raise NetworkError("ConnectionError")

    def delete_webhook(self, timeout=(5, 10)) -> bool | None:
        """This service is used to remove the web hook set for the arm.

        Args:
            timeout (tuple, int): Defaults to (5, 10).

        Returns:
            bool: If done "True" If not "False"
        """
        if not isinstance(timeout, (tuple, int)):
            return None
        result = self.req("get", "deleteWebhook", timeout=timeout)
        if result is not None and result.json()["ok"]:
            return result.json()["result"]
        return False

    def send_message(self, chat_id: str, text: str = None, components=None, reply_to_message_id: str = None,
                     timeout=(5, 10)) -> Message | None:
        """This service is used to send text messages.
        
        Args:
            chat_id (int): Chat ID.
            text (str): Message Text. 
            components (bot.Components, dict): Message Components. 
            reply_to_message_id (str): Reply Message ID. 
            timeout (tuple, int): Defaults to (5, 10).
        Raises:
            :class:`bale.Error`
        Returns:
            :class:`bale.Message`: On success, the sent Message is returned.
        """

        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        json = {
            "chat_id": chat_id,
            "text": text
        }
        if components:
            if isinstance(components, Components):
                json["reply_markup"] = components.to_dict()
            else:
                json["reply_markup"] = components
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        message = self.req("post", "sendMessage", json, timeout=timeout)
        if message is not None:
            json = message.json()
            if json["ok"]:
                return Message.from_dict(data=message.json()["result"], bot=self)
        return None

    def send_invoice(self, chat_id: str, title: str, description: str, provider_token: str, prices: Price,
                     reply_to_message_id: str = None, photo_url: str = None, need_name: bool = False,
                     need_phone_number: bool = False, need_email: bool = False, need_shipping_address: bool = False,
                     is_flexible: bool = True, timeout=(5, 10)) -> Message | None:
        """You can use this service to send money request messages.
        Args:
            chat_id (str): Chat ID
            title (str): Invoice Title
            description (str): Invoice Description
            provider_token (str): You can use 3 methods to receive money: 1.Card number 2. Port number and acceptor number 3. Wallet number "Bale"
            prices (Price, dict)
            reply_to_message_id (str, optional): _description_. Defaults to None.
            photo_url (str, optional): Photo URL of Invoice. Defaults to None.
            need_name (bool, optional): Get a name from "User"?. Defaults to False.
            need_phone_number (bool, optional): Get a Phone number from "User"?. Defaults to False.
            need_email (bool, optional): Get a Email from "User"?. Defaults to False.
            need_shipping_address (bool, optional): Get a Shipping Address from "User"?. Defaults to False.
            is_flexible (bool, optional): Is the Invoice Photo Flexible to the Payment button?. Defaults to True.
            timeout (tuple, optional): Defaults to (5, 10).
        Returns:
            :class:`Bale.Message`
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        json = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "provider_token": provider_token
        }
        if isinstance(prices, Price):
            json["prices"] = [prices.to_dict()]
        elif isinstance(prices, list):
            key_list = []
            for i in prices:
                if type(i) is Price:
                    key_list.append(i.to_dict())
                else:
                    key_list.append(i)
            json["prices"] = key_list
        if photo_url:
            json["photo_url"] = photo_url
        json["need_name"] = need_name
        json["need_phone_number"] = need_phone_number
        json["need_email"] = need_email
        json["need_shipping_address"] = need_shipping_address
        json["is_flexible"] = is_flexible
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        message = self.req("post", "sendInvoice", data=json, timeout=timeout)
        if message is not None:
            json = message.json()
            if json["ok"]:
                return Message.from_dict(data=message.json()["result"], bot=self)
        return None

    def edit_message(self, chat_id: str, message_id: str, newtext: str, components=None,
                     timeout=(10, 30)) -> requests.Response:
        """You can use this service to edit text messages that you have already sent through the arm.
        
        Args:
            chat_id (str): Chat Id.
            message_id (str): Message Id.
            newtext (str): New Content For Message.
            components (:class:`bale.Components`, optional): Components. Defaults to None.
            timeout (tuple, optional): _description_. Defaults to (10, 30).
        Raises:
            :class:`bale.Error`
        Return:
            :class:`requests.Response`
        """
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": newtext
        }
        if components:
            data["reply_markup"] = components.to_dict() if isinstance(components, Components) else components

        result = self.req("post", "editMessageText", data=data, timeout=timeout)
        return result

    def delete_message(self, chat_id: str, message_id: str, timeout=(10, 30)) -> bool:
        """You can use this service to delete a message that you have already sent through the arm.
        
        In Channel or Group:
            If it is a group or channel Manager, it can delete a message from (group or channel).

        In private message (PV):
            If the message was sent by a bot, it can be deleted with this method

        Args:
            chat_id (str): Chat ID.
            message_id (str): Message ID
            timeout (tuple, int): Defaults to (10, 30).

        Return:
            bool: if done "True" if not "False"
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        result = self.req(method="GET", type="deletemessage", params={
            "chat_id": str(chat_id),
            "message_id": message_id
        }, timeout=timeout)
        result = result.json()
        return result["result"] if result["ok"] else False

    def get_chat(self, chat_id: str, timeout=(10, 30)) -> Chat | None:
        """This service can be used to receive personal information that has previously interacted with the arm.

        Args:
            chat_id (str): Chat Id.
            timeout (tuple, optional): TimeOut. Defaults to (10, 30).
        Raises:
            :class:`bale.Error`
        Return:
            :class:`bale.Chat`: On success, the sent Message is returned.
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"

        chat = self.req("get", "getchat", params={
            "chat_id": chat_id
        })
        if chat is not None:
            json = chat.json()
            if json["ok"]:
                return Chat.from_dict(json["result"], bot=self) if chat is not None else None
        return None

    def get_chat_member(self, chat_id: str, user_id: str, timeout=(10, 30)) -> "ChatMember" | None:
        """
            Args:
                chat_id (str): Group ID
                user_id (str): Member ID
                timeout (tuple, int) : Defaults to (10, 30).

            Returns:
                :class:`bale.ChatMember`
            Raises:
                :class:`bale.Error`
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        result = self.req(method="GET", type="getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        })
        if result is None:
            return None
        json_result: dict = result.json()
        if json_result["ok"]:
            member = ChatMember.from_dict(json_result["result"])
            return member
        return None

    def get_chat_members_count(self, chat_id: str, timeout=(10, 30)) -> int | None:
        """
            Args:
                chat_id (str): Group ID
                timeout (tuple, int) : Defaults to (10, 30).

            Returns:
                :int: Memeber Chat count
            Raises:
                :class:`bale.Error`
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        result = self.req(method="GET", type="getChatMembersCount", params={
            "chat_id": chat_id
        })
        if result is None:
            return None
        json_result: dict = result.json()
        if json_result["ok"]:
            return json_result["result"]
        return None

    def get_chat_administrators(self, chat_id: str, timeout=(10, 30)) -> list["ChatMember"] | None:
        """This service can be used to display admins of a group or channel.

        Args:
            chat_id (str): Group ID
            timeout (tuple, int): Defaults to (10, 30).
        Raises:
            :class:`bale.Error`
        Returns:
            List[:class:`bale.ChatMember`]
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        result = self.req("get", "getChatAdministrators", params={"chat_id": chat_id}, timeout=timeout)
        members = []
        if result:
            if result.json()["ok"]:
                for i in result.json()["result"]:
                    member = ChatMember.from_dict(data=i)
                    members.append(member)
                return members if members != [] else None
        return None

    def get_updates(self, timeout=(10, 30), offset: int = None, limit: int = None) -> list["Update"] | None:
        """Use this method to receive incoming updates using long polling. 

        Args:
            timeout (tuple, int, optional): Defaults to (10, 30).
            offset (int, optional): Defaults to None.
            limit (int, optional): Defaults to None.

        Raises:
            :class:`bale.Error`

        Returns:
            List[:class:`bale.Update`]
        """
        result = []
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"

        options = {}
        if offset is not None:
            options["offset"] = offset
        if limit is not None:
            options["limit"] = limit

        updates = self.req("post", "getupdates", options, timeout=timeout)
        if updates:
            if not updates.json()["ok"]:
                updates = updates.json()
                raise f"{updates['error_code']} | {updates['description']}"
            for i in updates.json()["result"]:
                if offset is not None and i["update_id"] < offset:
                    continue
                update = Update.from_dict(data=i, bot=self)
                result.append(update)
            return result if result is not None else None

        return None
