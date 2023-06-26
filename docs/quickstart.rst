Quick Start
==============

Create a Mini Bot
------------------

.. note::
    You should give the token received from `@botFather <https://ble.ir/botFather>`_ to the library by the token parameter.

.. code-block:: python3
    :caption: This is a Example (normal level)

    from bale import Bot, Update, Message, EventType

    client = Bot(token="Your Token")

    @client.listen(EventType.READY)
    async def when_bot_is_ready():
        print(client.user, "is Ready!")

    @client.listen(EventType.UPDATE)
    async def when_receive_update(update: Update):
        print(update.update_id, update.type)

    @client.listen(EventType.MESSAGE)
    async def when_receive_message(message: Message):
        await message.reply(text="Hi!")

    client.run()

.. code-block:: python3
    :caption: This is a Example (class level)

    import bale

    class BaleBot(bale.Bot):
        def __init__(self):
            super().__init__(token="Your Token")
            self.add_event(bale.EventType.MESSAGE, self.on_message)
            self.add_event(bale.EventType.UPDATE, self.on_update)

        async def on_message(self, message):
            if message.chat.type.is_private_chat():
                return await message.reply(f"Hi {message.author.mention}")

        async def on_update(self, update):
            print(update.type, update.update_id)

    bot = BaleBot()
    bot.run()
