import bale

bot = bale.Bot(token="Your Token")

@bot.listen("on_update")
async def on_update(update: bale.Update):
	print(update.update_id)

@bot.listen("on_message")
async def donate(message: bale.Message):
	if message.content == "/donate":
		await message.reply_invoice(title="Example Donate", description="Example Donate description", provider_token="6037************", prices=[bale.Price(label="Milk", amount=20000)])

"""There is a problem of receiving the message of money arrival by "Bale" web services!"""

bot.run()