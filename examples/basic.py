from bale import Bot, Update, Message

client = Bot(token="Your Token")

@client.event
async def on_ready():
	print(client.user.username, "is Ready!")

@client.event
async def on_update(update: Update):
	print(update.update_id)

@client.event
async def on_message(message: Message):
	if message.content == '/start': # to get caption or text of message
		await message.reply('Hi, from python-bale-bot to everyone!')
		if message.chat.is_group_chat:
			await message.reply("It's is a special Hi for groups!") # work when message sent in a group

# See https://docs.python-bale-bot.ir/en/stable/event.html to get more information about events!

client.run()
