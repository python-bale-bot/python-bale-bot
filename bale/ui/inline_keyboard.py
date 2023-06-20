from __future__ import annotations

class InlineKeyboard:
    """This object shows an inline keyboard (within the message).

    Attributes
    ----------
        text: str
            Label text on the button.
        callback_data: str
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified
            inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
        url: str
            HTTP url to be opened when the button is pressed. Defaults to None.
        switch_inline_query: str
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified
            inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
        switch_inline_query_current_chat: str
            If set, pressing the button will insert the bot's username and the specified inline query in the current chat's input field. Can be empty,
            in which case only the bot's username will be inserted. Defaults to None.
    """
    __slots__ = (
        "text", "callback_data", "url", "switch_inline_query", "switch_inline_query_current_chat"
    )

    def __init__(self, text: str, *, callback_data: str = None, url: str = None, switch_inline_query: str = None,
                 switch_inline_query_current_chat: str = None):
        self.text = text
        self.callback_data = callback_data if callback_data is not None else None
        self.url = url if url is not None else None
        self.switch_inline_query = switch_inline_query if switch_inline_query is not None else switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat if switch_inline_query_current_chat is not None else None

    @classmethod
    def from_dict(cls, data: dict):
        if not data.get("text") or not data.get("callback_data"):
            return None
        return cls(text=data["text"], callback_data=data.get("callback_data"), url=data.get("url"),
                   switch_inline_query=data.get("switch_inline_query"),
                   switch_inline_query_current_chat=data.get("switch_inline_query_current_chat"))

    def to_dict(self) -> dict:
        data = {
            "text": self.text
        }

        if self.callback_data:
            data["callback_data"] = self.callback_data

        if self.url:
            data["url"] = self.url

        if self.switch_inline_query:
            data["switch_inline_query"] = self.switch_inline_query

        if self.switch_inline_query_current_chat:
            data["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat

        return data
