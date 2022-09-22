import bale

bot = bale.Bot(token="Your Token")

@bot.event
async def on_update(update: bale.Update):
	print(update.update_id)

@bot.event
async def on_message(update: bale.Update, message: bale.Message):
	await message.reply(text="Hi!")

bot.run()