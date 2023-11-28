from bale import Bot, CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, MenuKeyboardMarkup, MenuKeyboardButton

client = Bot(token="Your Token")

@client.event
async def on_ready():
	print(client.user, "is Ready!")

@client.event
async def on_message(message: Message):
	if message.content == "/start":
		reply_markup = InlineKeyboardMarkup()
		reply_markup.add(InlineKeyboardButton(text="what is python-bale-bot?", callback_data="python-bale-bot:help"))
		reply_markup.add(InlineKeyboardButton(text="package site", url="https://python-bale-bot.ir"), row=2)
		reply_markup.add(InlineKeyboardButton(text="package GitHub", url="https://python-bale-bot.ir/github"), row=2)
		await message.reply(
			f"*Hi {message.author.first_name}, Welcome to python-bale-bot bot*",
			components=reply_markup
		)

	elif message.content == "/keyboard":
		await message.reply(
			f"*Hi {message.author.first_name}, Welcome to python-bale-bot bot*",
			components=MenuKeyboardMarkup().add(MenuKeyboardButton('package site')).add(MenuKeyboardButton('package github'))
		)

	elif message.content in [
		'package site',
		'package github'
	]:
		await message.reply(
			"{} is {}".format(message.content, {"package site": 'https://python-bale-bot.ir', "package github": 'https://python-bale-bot.ir/github'}[message.content]),
			components=MenuKeyboardMarkup() # to remove menu keyboards
		)

@client.event
async def on_callback(callback: CallbackQuery):
	if callback.data == "python-bale-bot:help":
		await callback.message.reply(
			"*python-bale-bot* is a Python library for building bots on the Bale messenger platform. Bale is a messaging app that provides a secure and private messaging experience for users. The python-bale-bot library provides a simple and easy-to-use interface for building bots on the Bale platform, allowing developers to create bots that can send and receive messages, handle events, and perform various actions on behalf of users."
		)

client.run()
