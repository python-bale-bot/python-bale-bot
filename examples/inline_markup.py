from bale import Bot, CallbackQuery, Message, Components, InlineKeyboard, EventType

client = Bot(token="Your Token")

@client.listen(EventType.READY)
async def when_bot_is_ready():
	print(client.user, "is Ready!")

@client.listen(EventType.MESSAGE)
async def when_receive_message(message: Message):
	if message.content == "/start":
		await message.reply(
			"Hey!",
			components=Components(inline_keyboards=[[
					InlineKeyboard("Send Hi", callback_data="send_hi")
				]])
		)

@client.listen(EventType.CALLBACK)
async def when_receive_callback(callback: CallbackQuery):
	if callback.data == "send_hi":
		await callback.message.reply(
			f"Hi {callback.user.first_name}"
		)

client.run()
