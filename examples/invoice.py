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

from bale import Message, Bot, LabeledPrice
from bale.handlers import CommandHandler, MessageHandler
from bale.checks import ChatType, SUCCESSFUL_PAYMENT

client = Bot(token="Your Token")

@client.listen('on_ready')
async def on_ready_handler():
    print(client.user, "is Ready!")

@client.handle(CommandHandler('invoice', check=~ChatType.CHANNEL))
async def on_message(message: Message):
    return await message.chat.send_invoice(
        title="Example Donate",
        description="Example Donate description",
        provider_token="6037************",
        payload=str(message.author.user_id),
        prices=[LabeledPrice(label="Milk", amount=20000)]
    )

@client.handle(MessageHandler(SUCCESSFUL_PAYMENT))
async def on_successful_payment(message: Message):
    print("We Receive an payment From {}".format(message.successful_payment.payload))

client.run()