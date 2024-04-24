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
from bale.checks import PHOTOS

client = Bot("Your Token")

@client.listen('on_ready')
async def on_ready_handler():
    print(client.user, "is Ready!")

@client.handle(CommandHandler('photo'))
async def photo_command(message: Message):
    return await message.reply_photo(photo='./attachment.png', caption="This is a simple photo")

@client.handle(MessageHandler(PHOTOS))
async def save_photo_handler(message: Message):
    file = open('./attachment.png', 'wb')
    await message.photos[0].save_to_memory(file)
    return await message.reply("I saved this image!")

client.run()
