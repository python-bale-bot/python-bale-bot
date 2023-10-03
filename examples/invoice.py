from bale import Message, Bot, Price, SuccessfulPayment

client = Bot(token="Your Token")

@client.event
async def on_ready():
	print(client.user, "is Ready!")

@client.event
async def on_message(message: Message):
	if message.content == "/donate":
		await message.chat.send_invoice(
			title="Example Donate",
			description="Example Donate description",
			provider_token="6037************",
			payload="{}".format(message.author.user_id),
			prices=[Price(label="Milk", amount=20000)]
		)

@client.event
async def on_successful_payment(successful_payment: SuccessfulPayment):
	print("We Receive an payment From {}".format(successful_payment.payload))

client.run()