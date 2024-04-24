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

from bale import Bot, Update, Message
from bale.handlers import BaseHandler, CommandHandler
from bale.checks import ChatType

client = Bot(token="Your Token")

@client.listen('on_ready')
async def on_ready_handler():
    print(client.user, "is Ready!")

@client.handle(BaseHandler())
async def update_handler(update: Update):
    print(update.update_id)

@client.handle(CommandHandler(['start', 'help'], check=ChatType.PRIVATE | ChatType.GROUP))
async def start_command(message: Message):
    return await message.reply("Hello {}!".format(message.author.mention or message.author.first_name))

# See https://docs.python-bale-bot.ir/en/stable/bale.handlers.html to get more information about events!

client.run()
