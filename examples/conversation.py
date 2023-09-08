import asyncio
from bale import Bot, Message, EventType

client = Bot(token="Your Token")

@client.listen(EventType.READY)
async def when_bot_is_ready():
    print(client.user, "is Ready!")

@client.listen(EventType.MESSAGE)
async def when_receive_message(message: Message):
    if message.content == '/give_name_without_timeout':
        await message.reply('what is your name?')
        def answer_checker(m: Message):
            return message.author == m.author and bool(message.text)
        answer_obj: Message = await client.wait_for('message', check=answer_checker)
        return answer_obj.reply(f'Your name is {answer_obj.content}')

    elif message.content == '/give_name_with_timeout':
        await message.reply('what is your name?')

        def answer_checker(m: Message):
            return message.author == m.author and bool(message.text)
        try:
            answer_obj: Message = await client.wait_for('message', check=answer_checker, timeout=10.0)
        except asyncio.TimeoutError:
            return await message.chat.send('No response received; Therefore, the operation was canceled.')
        else:
            return answer_obj.reply(f'Your name is {answer_obj.content}')

client.run()