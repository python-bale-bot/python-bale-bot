#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2024
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.

from bale import Bot, CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, MenuKeyboardMarkup, MenuKeyboardButton
from bale.handlers import MessageHandler, CommandHandler, CallbackQueryHandler
from bale.checks import Text, Data

client = Bot(token="Your Token")

@client.listen('on_ready')
async def on_ready_handler():
    print(client.user, "is Ready!")

@client.handle(CommandHandler('start'))
async def start_command(message: Message):
    reply_markup = InlineKeyboardMarkup()
    reply_markup.add(InlineKeyboardButton(text="what is python-bale-bot?", callback_data="help"))
    reply_markup.add(InlineKeyboardButton(text="package site", url="https://python-bale-bot.ir"), row=2)
    reply_markup.add(InlineKeyboardButton(text="package changelog", url="https://python-bale-bot.ir/changelog"), row=2)
    return await message.reply(
        f"*Hi {message.author.mention or message.author.first_name}, Welcome to python-bale-bot bot*",
        components=reply_markup
    )


@client.handle(CallbackQueryHandler(Data("help")))
async def on_callback(callback: CallbackQuery):
    return await callback.message.reply(
        "*python-bale-bot* is a Python library for building bots on the Bale messenger platform. "
        "Bale is a messaging app that provides a secure and private messaging experience for users. "
        "The python-bale-bot library provides a simple and easy-to-use interface for building bots on the Bale platform, "
        "allowing developers to create bots that can send and receive messages, handle events, "
        "and perform various actions on behalf of users."
    )

@client.handle(CommandHandler('keyboard'))
async def keyboard_command(message: Message):
    return await message.reply(
        f"Hi {message.author.mention or message.author.first_name}, Welcome to python-bale-bot bot",
        components=MenuKeyboardMarkup().add(MenuKeyboardButton('site')).add(MenuKeyboardButton('github'))
    )

@client.handle(MessageHandler(Text(['site', 'github'])))
async def menu_keyboard(message: Message):
    await message.reply(
        "https://python-bale-bot.ir"
        if message.text == 'site' else
        "https://python-bale-bot.ir/github",
        components=MenuKeyboardMarkup()  # to remove menu keyboards
    )

client.run()
