import bale

bot = bale.Bot(token="Your Token")

@bot.event
async def on_update(update: bale.Update):
	print(update.update_id)

@bot.event
async def on_message(update: bale.Update, message: bale.Message):
	if message.content == "/donate":
		await message.reply_invoice(title="Example Donate", description="Example Donate description", provider_token="6037************", prices=[bale.Price(label="Milk", amount=20000)])

"""There is a problem of receiving the message of money arrival by "Bale" web services!"""

bot.run()