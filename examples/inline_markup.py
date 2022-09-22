import bale

bot = bale.Bot(token="Your Token")

@bot.event
async def on_update(update: bale.Update):
	print(update.update_id)


@bot.event
async def on_message(update: bale.Update, message: bale.Message):
	await message.reply(text="Hi {}\nThis is a Components!".format(message.author.first_name), components=bale.Components(inline_keyboards=[[bale.InlineKeyboard(text="Test", callback_data="test_component")]]))

@bot.event
async def on_callback(update: bale.update, callback: bale.CallbackQuery):
	await callback.from_user.send("Button Clicked!")

bot.run()