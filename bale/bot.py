from __future__ import annotations
import asyncio
from bale import (Message, Update, User, Components, Chat, Price, ChatMember, HTTPClient)


__all__ = (
    "Bot"
)


class _Loop:
    __slots__ = ()
    
    
_loop = _Loop()


class Bot:
    """This object represents a Bale Bot.

        Args:
            token (str): Bot Token.
                
        Raises:
            :class:`bale.Error`
    """
    __slots__ = (
        "loop",
        "token",
        "loop",
        "_user",
        "http",
        "_closed"
    )

    def __init__(self, token: str, **kwargs):
        self.loop = _loop
        self.token = token
        self.http: HTTPClient = HTTPClient(loop=self.loop, connector=kwargs.get("connector"), token=token)
        self._user = None
        self._closed = False

    async def __aenter__(self):
        loop = asyncio.get_running_loop()
        self.loop = loop
        self.http.loop = loop
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if not self.is_closed():
            self._closed = True

    def is_closed(self):
        """:class:`bool`: Connection Status"""
        return self._closed

    def _get_bot(self) -> User:
        """Get Bot.

        Returns:
            :class:`Bale.User`: Bot User information.
        Raises:
            :class:`Bale.Error`
        """
        response, payload = self.http.get_bot()
        return User.from_dict(data=payload.get("result"), bot=self)

    @property
    def user(self) -> User:
        """Get Bot User

        Returns:
            :class:`bale.User`
        Raises:
            :class:`Bale.Error`
        """
        if self._user is None:
            self._user = self._get_bot()
        return self._user

    async def delete_webhook(self) -> bool:
        """This service is used to remove the web hook set for the arm.

        Returns:
            bool: If done "True" If not "False"
        """
        response, payload = await self.http.delete_webhook()
        return payload["result"]

    async def send_message(self, chat_id: str, text: str = None, components=None, reply_to_message_id: str = None) -> Message | None:
        """This service is used to send text messages.
        
        Args:
            chat_id (int): Chat ID.
            text (str): Message Text. 
            components (bot.Components, dict): Message Components. 
            reply_to_message_id (str): Reply Message ID. 
        Raises:
            :class:`bale.Error`
        Returns:
            :class:`bale.Message`: On success, the sent Message is returned.
        """
        if components:
            if isinstance(components, Components):
                components = components.to_dict()
            else:
                components = components
        if reply_to_message_id:
            reply_to_message_id = reply_to_message_id
        response, payload = await self.http.send_message(chat_id, text, components=components, reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=payload["result"], bot=self)

    async def send_invoice(self, chat_id: str, title: str, description: str, provider_token: str, prices: Price, photo_url: str = None, need_name: bool = False, need_phone_number: bool = False, need_email: bool = False, need_shipping_address: bool = False, is_flexible: bool = True) -> Message | None:
        """You can use this service to send money request messages.
        Args:
            chat_id (str): Chat ID
            title (str): Invoice Title
            description (str): Invoice Description
            provider_token (str): You can use 3 methods to receive money: 1.Card number 2. Port number and acceptor number 3. Wallet number "Bale"
            prices (Price, dict)
            photo_url (str, optional): Photo URL of Invoice. Defaults to None.
            need_name (bool, optional): Get a name from "User"?. Defaults to False.
            need_phone_number (bool, optional): Get a Phone number from "User"?. Defaults to False.
            need_email (bool, optional): Get a Email from "User"?. Defaults to False.
            need_shipping_address (bool, optional): Get a Shipping Address from "User"?. Defaults to False.
            is_flexible (bool, optional): Is the Invoice Photo Flexible to the Payment button?. Defaults to True.
        Returns:
            :class:`Bale.Message`
        """
        if isinstance(prices, Price):
            prices = [prices.to_dict()]
        # create a function for convert key_lists in message, components
        elif isinstance(prices, list):
            key_list = []
            for i in prices:
                if type(i) is Price:
                    key_list.append(i.to_dict())
                else:
                    key_list.append(i)
            prices = key_list
        response, payload = await self.http.send_invoice(chat_id, title, description, provider_token, prices, photo_url, need_name, need_phone_number, need_email, need_shipping_address, is_flexible)
        return Message.from_dict(data=payload["result"], bot=self)

    async def edit_message(self, chat_id: str, message_id: str, text: str, components=None) -> Message:
        """You can use this service to edit text messages that you have already sent through the arm.
        
        Args:
            chat_id (str): Chat Id.
            message_id (str): Message Id.
            text (str): New Content For Message.
            components (:class:`bale.Components`, optional): Components. Defaults to None.
        Raises:
            :class:`bale.Error`
        Return:
            :class:`requests.Response`
        """
        if components:
            components = components.to_dict() if isinstance(components, Components) else components

        response, payload = await self.http.edit_message_text(chat_id, message_id, text, components)
        return payload

    async def delete_message(self, chat_id: str, message_id: str) -> bool:
        """You can use this service to delete a message that you have already sent through the arm.
        
        In Channel or Group:
            If it is a group or channel Manager, it can delete a message from (group or channel).

        In private message (PV):
            If the message was sent by a bot, it can be deleted with this method

        Args:
            chat_id (str): Chat ID.
            message_id (str): Message ID
        Return:
            bool: if done "True" if not "False"
        """
        response, payload = await self.http.delete_message(chat_id, message_id)
        return payload["result"]

    async def get_chat(self, chat_id: str) -> Chat:
        """This service can be used to receive personal information that has previously interacted with the arm.

        Args:
            chat_id (str): Chat Id.
        Raises:
            :class:`bale.Error`
        Return:
            :class:`bale.Chat`: On success, the sent Message is returned.
        """
        response, payload = await self.http.get_chat(chat_id)
        return Chat.from_dict(payload["result"], bot=self)

    async def get_chat_member(self, chat_id: str, user_id: str) -> "ChatMember":
        """
            Args:
                chat_id (str): Group ID
                user_id (str): Member ID
            Returns:
                :class:`bale.ChatMember`
            Raises:
                :class:`bale.Error`
        """
        response, payload = await self.http.get_chat_member(chat_id=chat_id, member_id=user_id)
        return ChatMember.from_dict(payload["result"])

    async def get_chat_members_count(self, chat_id: str) -> int:
        """
            Args:
                chat_id (str): Group ID
            Returns:
                :int: Member Chat count
            Raises:
                :class:`bale.Error`
        """
        response, payload = await self.http.get_chat_members_count(chat_id)
        return payload["result"]

    async def get_chat_administrators(self, chat_id: str) -> list["ChatMember"]:
        """This service can be used to display admins of a group or channel.

        Args:
            chat_id (str): Group ID
        Raises:
            :class:`bale.Error`
        Returns:
            List[:class:`bale.ChatMember`]
        """
        response, payload = await self.http.get_chat_administrators(chat_id)
        members = []
        for member_payload in payload["result"]:
            members.append(ChatMember.from_dict(data=member_payload))
        return members

    async def get_updates(self, offset: int = None, limit: int = None) -> list["Update"] | None:
        """Use this method to receive incoming updates using long polling.

        Args:
            offset (int, optional): Defaults to None.
            limit (int, optional): Defaults to None.
        Raises:
            :class:`bale.Error`

        Returns:
            List[:class:`bale.Update`]
        """
        response, payload = await self.http.get_updates(offset, limit)
        updates = []
        for update_payload in payload.get("result"):
            if offset is not None and update_payload.get("update_id") < offset:
                continue
            update = Update.from_dict(data=update_payload, bot=self)
            updates.append(update)
        return updates

    async def run(self):
        async def main():
            async with self:
                self._user = self._get_bot()

        asyncio.run(main())
