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
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, TypedDict

if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .chat import Chat
    from .contact import Contact
    from .files import Animation, Audio, Document, PhotoSize, Video, Voice
    from .invoice import Invoice
    from .location import Location
    from .markup import InlineKeyboardMarkup
    from .poll import Poll
    from .sticker import Sticker
    from .successfulpayment import SuccessfulPayment
    from .user import User
    from .webapp import WebAppData


__all__ = ("Message", "MessageEntity")


class MessageEntity(TypedDict):
    type: str
    offset: int
    length: int


class Message(TypedDict, total=False):
    message_id: int
    date: int
    chat: NotRequired["Chat | None"]
    from_user: NotRequired["User | None"]
    text: NotRequired[str | None]
    caption: NotRequired[str | None]
    entities: NotRequired[list["MessageEntity"] | None]
    caption_entities: NotRequired[list["MessageEntity"] | None]
    photo: NotRequired[list["PhotoSize"] | None]
    document: NotRequired["Document | None"]
    video: NotRequired["Video | None"]
    audio: NotRequired["Audio | None"]
    voice: NotRequired["Voice | None"]
    animation: NotRequired["Animation | None"]
    sticker: NotRequired["Sticker | None"]
    poll: NotRequired["Poll | None"]
    contact: NotRequired["Contact | None"]
    location: NotRequired["Location | None"]
    invoice: NotRequired["Invoice | None"]
    successful_payment: NotRequired["SuccessfulPayment | None"]
    web_app_data: NotRequired["WebAppData | None"]
    reply_to_message: NotRequired["Message | None"]
    reply_markup: NotRequired["InlineKeyboardMarkup | None"]
    message_thread_id: NotRequired[int | None]
    media_group_id: NotRequired[str | None]
    forward_from: NotRequired["User | None"]
    forward_from_chat: NotRequired["Chat | None"]
    forward_from_message_id: NotRequired[int | None]
    forward_date: NotRequired[int | None]
    is_automatic_forward: NotRequired[bool | None]
    edit_date: NotRequired[int | None]
    new_chat_members: NotRequired[list["User"] | None]
    left_chat_member: NotRequired["User | None"]
