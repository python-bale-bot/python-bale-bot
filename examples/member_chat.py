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

from bale import Bot, Message
from bale.handlers import CommandHandler, MessageHandler
from bale.checks import NEW_CHAT_MEMBERS, LEFT_CHAT_MEMBER, Chat

client = Bot(token='Your Token')
CHAT_ID = 1234

@client.listen('on_ready')
async def on_ready_handler():
    print(client.user, "is Ready!")

@client.handle(CommandHandler('members', Chat(CHAT_ID)))
async def members_command(message: Message):
    members_count = await message.chat.get_members_count()
    return await message.reply(f"The {message.chat.title} has {members_count} members!")

@client.handle(MessageHandler(Chat(client.user.chat_id) & NEW_CHAT_MEMBERS))
async def new_chat_members_handle(message: Message):
    for user in message.new_chat_members:
        if user == client.user:
            continue

        await message.chat.send("Welcome {} to {}!".format(
            user.mention or user.first_name,
            message.chat.title
        ), delete_after=180.0)

@client.handle(MessageHandler(Chat(client.user.chat_id) & LEFT_CHAT_MEMBER))
async def left_chat_member_handler(message: Message):
    left_chat_member = message.left_chat_member
    if left_chat_member == client.user:
        return

    await message.chat.send(f"The {left_chat_member.first_name} leaved from chat", delete_after=20.0)

client.run()
