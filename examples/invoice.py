from bale import Message, Bot, LabeledPrice
from bale.handlers import CommandHandler, MessageHandler
from bale.checks import ChatType, SUCCESSFUL_PAYMENT

client = Bot(token="Your Token")

@client.event
async def on_ready():
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