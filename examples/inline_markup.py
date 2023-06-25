from bale import Bot, CallbackQuery, Message, Components, InlineKeyboard, EventType

client = Bot(token="Your Token")

@client.listen(EventType.READY)
async def when_bot_is_ready():
	print(client.user, "is Ready!")

@client.listen(EventType.MESSAGE)
async def when_receive_message(message: Message):
	if message.content == "/start":
		component = Components()
		component.add_inline_keyboard(InlineKeyboard(text="what is python-bale-bot?", callback_data="python-bale-bot:help"))
		component.add_inline_keyboard(InlineKeyboard(text="package site", url="https://python-bale-bot.ir"), row=2)
		component.add_inline_keyboard(InlineKeyboard(text="package GitHub", url="https://python-bale-bot.ir/github"), row=2)
		await message.reply(
			f"*Hi {message.author.first_name}, Welcome to python-bale-bot bot*",
			components=component
		)

@client.listen(EventType.CALLBACK)
async def when_receive_callback(callback: CallbackQuery):
	if callback.data == "python-bale-bot:help":
		await callback.message.reply(
			"*python-bale-bot* is a Python library for building bots on the Bale messenger platform. Bale is a messaging app that provides a secure and private messaging experience for users. The python-bale-bot library provides a simple and easy-to-use interface for building bots on the Bale platform, allowing developers to create bots that can send and receive messages, handle events, and perform various actions on behalf of users."
		)

client.run()
