from bale import Bot, Message, Chat, User

client = Bot(token='Your Token')
CHAT_ID = 1234


@client.event
async def on_ready():
    print(client.user.username, "is Ready!")


@client.event
async def on_message(message: Message):
    if int(message.chat.id) == CHAT_ID and message.content == '/members':
        members_count = await message.chat.get_chat_members_count()
        return await message.reply("The {} has {} members!".format(
            message.chat.title,
            members_count
        ))


@client.event
async def on_member_chat_join(message: Message, chat: Chat, user: User):
    if user == client.user:
        return
    await chat.send("Welcome {} to {}!".format(
        user.mention or user.first_name,
        chat.title
    ), delete_after=180.0)


@client.event
async def on_member_chat_leave(message: Message, chat: Chat, user: User):
    if user == client.user:
        return
    await chat.send("Bye {}!".format(
        user.mention or user.first_name
    ), delete_after=20.0)


client.run()
