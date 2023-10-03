from bale import Bot, Update, Message

client = Bot(token="Your Token")

@client.event
async def on_ready():
	print(client.user, "is Ready!")

@client.event
async def on_update(update: Update):
	print(update.update_id, update.type)

@client.event
async def on_message(message: Message):
	await message.reply(text="Hi!")

client.run()
