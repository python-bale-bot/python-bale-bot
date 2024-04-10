from bale import Bot, Update, Message
from bale.handlers import BaseHandler, CommandHandler
from bale.checks import ChatType

client = Bot(token="Your Token")

@client.event
async def on_ready():
	print(client.user.username, "is Ready!")

@client.handle(BaseHandler())
async def update_handler(update: Update):
	print(update.update_id)

@client.handle(CommandHandler(['start', 'help'], check=ChatType.PRIVATE | ChatType.GROUP))
async def start_command(message: Message):
	return await message.reply("Hello %s!".format(message.author.mention or message.author.first_name))

# See https://docs.python-bale-bot.ir/en/stable/bale.handlers.html to get more information about events!

client.run()
