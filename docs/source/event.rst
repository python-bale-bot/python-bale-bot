Event Reference
===============

**The list of events that can be received by the bot.**

An example of how to listen to events in different situations (for ``on_message`` event):

.. code:: python

    from bale import Bot, Message

    bot = Bot("YOUR_TOKEN")

    @bot.event
    async def on_message(message: Message):
        if message.content == '/start':
            return await message.reply("Hi, python-bale-bot!")

    bot.run()

.. code:: python

    from bale import Bot, Message

    class MyBot(Bot):
        async def on_message(self, message: Message):
            if message.content == '/start':
                return await message.reply("Hi, python-bale-bot!")

    MyBot('YOUR_TOKEN').run()

Connection
~~~~~~~~~~

.. py:function:: on_before_ready()
    :async:

    This event is called before the updater starts.

.. py:function:: on_ready()

    When the updater starts working and the Bot information is placed in :attr:`bale.Bot.user`.

Updates
~~~~~~~

.. py:function:: on_update(update)
    :async:

    This event is called when an update is received from "Bale" servers.

    :param update: update received.
    :type update: :class:`bale.Update`

Messages
~~~~~~~~

.. py:function:: on_message(message)
    :async:

    This event is called when sending a message in a chat to which the bot is connected.

    :param message: message sent.
    :type message: :class:`bale.Message`

.. py:function:: on_message_edit(message)
    :async:

    This event is called when the sent message is edited.

    :param message: message edited.
    :type message: :class:`bale.Message`

CallbackQuery
~~~~~~~~~~~~~

.. py:function:: on_callback(callback)
    :async:

    This event is called when a callback query is created.

    :param callback: callback received.
    :type callback: :class:`bale.CallbackQuery`

Groups
~~~~~~

.. py:function:: on_member_chat_join(message, chat, user)
    :async:

    This event is called when a user joins the chat.

    :param message: message sent.
    :type message: :class:`bale.Message`
    :param chat: the chat.
    :type chat: :class:`bale.Chat`
    :param user: the user.
    :type user: :class:`bale.User`

.. py:function:: on_member_chat_leave(message, chat, user)
    :async:

    This event is called when a user leaves the chat.

    :param message: message sent.
    :type message: :class:`bale.Message`
    :param chat: the chat.
    :type chat: :class:`bale.Chat`
    :param user: the user.
    :type user: :class:`bale.User`

Payments
~~~~~~~~

.. py:function:: on_successful_payment(payment)
    :async:

    This event is called when a transaction is completed and its status is successful.

    :param successful_payment: the payment.
    :type successful_payment: :class:`bale.SuccessfulPayment`