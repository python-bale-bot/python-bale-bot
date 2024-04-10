from bale import Bot, Message
from bale.handlers import CommandHandler, MessageHandler
from bale.checks import NEW_CHAT_MEMBERS, LEFT_CHAT_MEMBER, Chat

client = Bot(token='Your Token')
CHAT_ID = 1234

@client.event
async def on_ready():
    print(client.user.username, "is Ready!")

@client.handle(CommandHandler('members', Chat(CHAT_ID)))
async def members_command(message: Message):
    members_count = await message.chat.get_chat_members_count()
    return await message.reply("The {} has {} members!".format(
        message.chat.title,
        members_count
    ))

@client.handle(MessageHandler(Chat(client.user.chat_id) & NEW_CHAT_MEMBERS))
async def new_chat_members_handle(message: Message):
    for user in message.new_chat_members:
        if user == client.user:
            continue

        await message.chat.send("Welcome {} to {}!".format(
            user.mention or user.first_name,
            message.chat.title
        ), delete_after=180.0)

@client.handle(MessageHandler(Chat(client.user.chat_id) & LEFT_CHAT_MEMBER))
async def left_chat_member_handler(message: Message):
    left_chat_member = message.left_chat_member
    if left_chat_member == client.user:
        return

    await message.chat.send("Bye {}!".format(
        left_chat_member.first_name
    ), delete_after=20.0)

client.run()
