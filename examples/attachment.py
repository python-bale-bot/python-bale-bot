from bale import Bot, Message, EventType

client = Bot("Your Token")

@client.listen(EventType.READY)
async def when_bot_is_ready():
    print(client.user, "is Ready!")
    
@client.listen(EventType.MESSAGE)
async def when_receive_message(message: Message):
    if message.content == "/photo":
        photo = open('attachment.png', 'rb').read()
        return await message.reply_photo(photo=photo, caption="This is a simple photo")

    elif message.attachment and message.photos:
        file = open('./attachment.{}'.format(message.attachment.mime_type), 'wb')
        await message.attachment.save_to_memory(file)
        return await message.reply("I saved this image!")

client.run()
