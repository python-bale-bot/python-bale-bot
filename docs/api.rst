.. currentmodule:: bale

API Reference
==============

Version Info
------------

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.


Bot
----

.. attributetable:: bale.Bot

.. autoclass:: bale.Bot()
   :members:
   :inherited-members:

Models
------

CallbackQuery
~~~~~~~~~~~~~

.. attributetable:: bale.CallbackQuery

.. autoclass:: bale.CallbackQuery()
   :members:

Chat
~~~~

.. attributetable:: bale.Chat

.. autoclass:: bale.Chat()
   :members:

Chat Type
~~~~~~~~~~~
.. autoclass:: bale.ChatType()
   :members:

User
~~~~~

.. attributetable:: bale.User

.. autoclass:: bale.User()
   :members:

ChatMember
~~~~~~~~~~

.. attributetable:: bale.ChatMember

.. autoclass:: bale.ChatMember()
   :members:

MemberRole
~~~~~~~~~~
.. autoclass:: bale.MemberRole()
   :members:

Message
~~~~~~~

.. attributetable:: bale.Message

.. autoclass:: bale.Message()
   :members:

Update
~~~~~~

.. attributetable:: bale.Update

.. autoclass:: bale.Update()
   :members:   

Update Type
~~~~~~~~~~~
.. autoclass:: bale.UpdateType()
   :members:

Components
~~~~~~~~~~

.. attributetable:: bale.Components

.. autoclass:: bale.Components()
   :members: 

Inline Keyboard
~~~~~~~~~~~~~~~

.. attributetable:: bale.InlineKeyboard

.. autoclass:: bale.InlineKeyboard()
   :members:


Keyboard
~~~~~~~~

.. attributetable:: bale.Keyboard

.. autoclass:: bale.Keyboard()
   :members:

Remove Components
~~~~~~~~~~~~~~~~~~

.. attributetable:: bale.RemoveComponents

.. autoclass:: bale.RemoveComponents()
   :members:


Attachment Models
-----------------

Audio
~~~~~

.. attributetable:: bale.Audio

.. autoclass:: bale.Audio()
   :members:


Contact Message
~~~~~~~~~~~~~~~

.. attributetable:: bale.ContactMessage

.. autoclass:: bale.ContactMessage()
   :members:

Document
~~~~~~~~

.. attributetable:: bale.Document

.. autoclass:: bale.Document()
   :members:


Photo
~~~~~

.. attributetable:: bale.Photo

.. autoclass:: bale.Photo()
   :members:

Location
~~~~~~~~

.. attributetable:: bale.Location

.. autoclass:: bale.Location()
   :members:

Payment Models
--------------

Invoice
~~~~~~~~

.. attributetable:: bale.Invoice

.. autoclass:: bale.Invoice()
   :members:


Price
~~~~~

.. attributetable:: bale.Price

.. autoclass:: bale.Price()
   :members:



Event Reference
---------------

Event Types
~~~~~~~~~~~

.. attributetable:: bale.EventType

.. autoclass:: bale.EventType()
   :members:

.. note::
    You can use :class:`bale.EventType` for Events.

.. code-block:: python3

    from bale import Bale, EventType

    bot = bale.Bot(token="Your Token")

    @bot.listen(EventType.Update)
    async def when_receive_update(update):
        ...

Before Ready
~~~~~~~~~~~~

.. function:: on_before_ready()

   Called Before the :class:`bale.Updater` stars.

Ready
~~~~~

.. function:: on_ready()

   Called when a bot is ready.

Update
~~~~~~~

.. function:: on_update(update)

   Called when a Update Sent.

   :param update: The update
   :type update: :class:`bale.Update`

Message
~~~~~~~~

.. function:: on_message(message)

   Called when a Message Sent.

   :param message: The message
   :type message: :class:`bale.Message`

Callback
~~~~~~~~

.. function:: on_callback(callback)

   Called when a Callback Sent.

   :param callback: The callback
   :type callback: :class:`bale.CallbackQuery`

Member Chat Join
~~~~~~~~~~~~~~~~

.. function:: on_member_chat_join(chat, user)

   When a user joins the chat.

   :param chat: The Chat
   :type chat: :class:`bale.Chat`
   :param user: The user who entered the chat
   :type user: :class:`bale.User`

Member Chat Leave
~~~~~~~~~~~~~~~~

.. function:: on_member_chat_leave(chat, user)

   When a user leaves the chat.

   :param chat: The Chat
   :type chat: :class:`bale.Chat`
   :param user: The user who leaved the chat
   :type user: :class:`bale.User`

Exceptions
------------

The following exceptions are thrown by the library.

.. autoexception:: BaleError
    :members:

.. autoexception:: InvalidToken

.. autoexception:: APIError

.. autoexception:: NetworkError

.. autoexception:: TimeOut

.. autoexception:: NotFound

.. autoexception:: Forbidden

.. autoexception:: RateLimited

.. autoexception:: HTTPException
