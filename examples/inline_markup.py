import bale

bot = bale.Bot(token="Your Token")

@bot.listen("on_update")
async def on_update(update: bale.Update):
	print(update.update_id)

@bot.listen("on_message")
async def on_message(message: bale.Message):
	await message.reply(text="Hi {}\nThis is a Components!".format(message.author.first_name), components=bale.Components(inline_keyboards=[[bale.InlineKeyboard(text="Test", callback_data="test_component")]]))

@bot.listen("on_callback")
async def on_callback(callback: bale.CallbackQuery):
	await callback.from_user.send("Button Clicked!")

bot.run()