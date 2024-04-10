import asyncio
from bale import Bot, Update, Message
from bale.handlers import CommandHandler
from bale.checks import Author, TEXT

client = Bot(token="Your Token")

@client.event
async def on_ready():
    print(client.user, "is Ready!")

@client.handle(CommandHandler('give_name_without_timeout'))
async def conversation_handler(message: Message):
    await message.reply('what is your name?')
    received_update: Update = await client.wait_for(Author(message.author.id) & TEXT)
    return await received_update.message.reply(f'Your name is {received_update.message.text}')

@client.handle(CommandHandler('give_name_with_timeout'))
async def conversation_handler_2(message: Message):
    await message.reply('what is your name?')

    try:
        received_update: Update = await client.wait_for(Author(message.author.id) & TEXT, timeout=10.0)
    except asyncio.TimeoutError:
        return await message.chat.send('No response received; Therefore, the operation was canceled.')
    else:
        return await received_update.message.reply(f'Your name is {received_update.message.text}')

client.run()
