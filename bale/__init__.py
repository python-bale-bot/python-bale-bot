"""
MIT License

Copyright (c) 2023 Kian Ahmadian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from .version import __version__
from .request import HTTPClient, Route, ResponseStatusCode, ResponseParser
from .ui import InlineKeyboard, MenuKeyboard, RemoveMenuKeyboard, Components
from .attachments import File, Audio, ContactMessage, Location, Photo, Document, Video, InputFile
from .payments import Price, Invoice
from .user import User
from .attachments.contact import ContactMessage
from .chat import Chat, ChatType
from .message import Message
from .permissions import Permissions
from .chatmember import ChatMember, ChatMemberStatus
from .callbackquery import CallbackQuery
from .update import Update, UpdateType
from .updater import Updater, EventType
from .error import BaleError, APIError, NetworkError, HTTPException, TimeOut, NotFound, Forbidden, HTTPClientError, InvalidToken, RateLimited
from .bot import Bot

__title__ = "python-bale-bot"
__author__ = "Kian Ahmadian"
__copyright__ = 'Copyright 2021-present Kian Ahmadian'
__license__ = 'MIT'
