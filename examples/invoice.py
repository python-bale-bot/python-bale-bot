from bale import Update, Message, Bot, Price, EventType

client = Bot(token="Your Token")

@client.listen(EventType.READY)
async def when_bot_is_ready():
	print(client.user, "is Ready!")

@client.listen(EventType.UPDATE)
async def when_receive_update(update: Update):
	print(update.update_id, update.type)

@client.listen(EventType.MESSAGE)
async def when_receive_message(message: Message):
	if message.content == "/donate":
		await message.reply_invoice(
			title="Example Donate",
			description="Example Donate description",
			provider_token="6037************",
			prices=[Price(label="Milk", amount=20000)]
		)

"""There is a problem of receiving the message of money arrival by 'Bale' web services!"""

client.run()