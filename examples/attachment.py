from bale import Bot, Message, InputFile

client = Bot("Your Token")

@client.event
async def on_ready():
    print(client.user, "is Ready!")
    
@client.event
async def on_message(message: Message):
    if message.content == "/photo":
        file = open('attachment.png', 'rb').read()
        photo = InputFile(file)
        return await message.reply_photo(photo=photo, caption="This is a simple photo")

    elif message.attachment and message.photos:
        file = open('./attachment.png', 'wb')
        await message.attachment.save_to_memory(file)
        return await message.reply("I saved this image!")

client.run()
