from bale import Bot, Update, Message, EventType

client = Bot(token="Your Token")

@client.listen(EventType.READY)
async def when_bot_is_ready():
	print(client.user, "is Ready!")

@client.listen(EventType.UPDATE)
async def when_receive_update(update: Update):
	print(update.update_id, update.type)

@client.listen(EventType.MESSAGE)
async def when_receive_message(message: Message):
	await message.reply(text="Hi!")

client.run()
