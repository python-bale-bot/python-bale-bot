import bale

bot = bale.Bot(token="Your Token")

@bot.listen("on_ready")
async def on_ready():
	print(bot.user, "is Ready!")

@bot.listen("on_update")
async def on_update(update: bale.Update):
	print(update.update_id)

@bot.listen("on_message")
async def on_message(message: bale.Message):
	await message.reply(text="Hi!")

bot.run()