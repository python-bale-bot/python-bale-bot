from bale import Bot, Message
from bale.handlers import CommandHandler, MessageHandler
from bale.checks import PHOTOS

client = Bot("Your Token")

@client.event
async def on_ready():
    print(client.user, "is Ready!")

@client.handle(CommandHandler('photo'))
async def photo_command(message: Message):
    return await message.reply_photo(photo='./attachment.png', caption="This is a simple photo")

@client.handle(MessageHandler(PHOTOS))
async def save_photo_handler(message: Message):
    file = open('./attachment.png', 'wb')
    await message.photos[0].save_to_memory(file)
    return await message.reply("I saved this image!")

client.run()
