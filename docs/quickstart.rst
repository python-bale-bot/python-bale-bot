Quick Start
==============

Create a Mini Bot
------------------

.. code-block:: python3
    :caption: This is a Example (normal level)

    import bale

    bot = bale.Bot(token="Your Token")

    @bot.listen("on_update")
    async def update(update):
        print(update.update_id)

    @bot.listen("on_message")
    async def message(message):
        await message.reply("Hi!")

.. code-block:: python3
    :caption: This is a Example (class level)

    import bale

    class BaleBot(bale.Bot):
        def __init__(self):
            super().__init__(token="Your Token")
            self.add_event("on_message", self.on_message)
            self.add_event("on_update", self.on_update)


        async def on_message(self, message):
            if message.chat.type.is_private_chat():
                return await message.reply(f"Hi {message.author.mention}")

        async def on_update(self, update):
            print(update.type, update.update_id)


    bot = BaleBot()
    bot.run()
