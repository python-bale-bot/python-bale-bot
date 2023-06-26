.. currentmodule::bale

Change Log
==========

Project changes are shown on this page.

v2.4.6
------

New Features
~~~~~~~~~~~~

- Components have been moved to `ui`
- Improve the process of using Components and Files
- Add new method :meth:`bale.Bot.send_audio`
- Support from `400` status code Errors in :class:`bale.HTTPClient`
- Full support from "Bale" rate limits
- Add :attr:`bale.Message.attachment`, :attr:`bale.Components.menu_keyboards`, :attr:`bale.Components.inline_keyboards`
- Update License to LGP
- Improve documentation
- Update `examples <https://github.com/python-bale-bot/python-bale-bot/tree/master/examples>`_ directory

Bug Fixes
~~~~~~~~~~

- Fix bug of stopping the Bot
- Fix the problem of :meth:`bale.Bot.send_invoice` & :meth:`bale.Bot.send_video` checkers

v2.4.5
------

New Features
~~~~~~~~~~~~

- Improve documentation
- Add new methods (:meth:`bale.Bot.forward_message`, :meth:`bale.Bot.ban_chat_member`, :meth:`bale.Bot.send_video`)
- Add new event :meth:`bale.Bot.on_edited_message`

Bug Fixes
~~~~~~~~~~

- Fix bugs in parse Updates
- Updater.__lock bug
- :attr:`bale.Update.type` bugs
- Fix :attr:`bale.Chat.invite_link` bugs
- Improving the :class:`bale.Message` class (`__eq__`, `__ne__`, `__repr__`)
- Add new type `channel` to :class:`bale.ChatType`

v2.4.4
------

New Features
~~~~~~~~~~~~

- Improve the :class:`bale.RateLimit` object
- Add new :class:`bale.Updater`
- Adding the method of :meth:`bale.Bot.send_location` and :meth:`bale.Bot.send_contact`
- Update Readme file

Bug Fixes
~~~~~~~~~~

- Fix `http` error
- Fix `bale.EventType.BEFORE_READY` and :meth:`bale.on_before_ready` bug
- Fix bot closing problem

v2.4.3
------

Bug Fixes
~~~~~~~~~~

- Changes in some functions and commands
- Add :meth:`bale.Bot.download_file` for Download files with `file_id`
- Update `LICENSE`
- Improve Code Quality

v2.4.2
------

Bug Fixes
~~~~~~~~~~

- Changes in some functions and commands
- Improve Code Quality

v2.4.1
------

New Features
~~~~~~~~~~~~

- Add ``updater`` param to :class:`bale.Bot` for Custom-Updater
- Add :attr:`bale.Message.type` & support :class:`bale.UpdateType` from it
- Update Readme file

Bug Fixes
~~~~~~~~~~

- Improve Code Quality


v2.4.0
------

New Features
~~~~~~~~~~~~

- New changes for better Connections
- Synchronization of Exceptions with document
- Add Support from local rate limits
- Add support from :class:`bale.HTTPClient` errors

Advance
~~~~~~~

- Add a Response Parser for connections
- Add Type Checker to All functions
- Add new supporter class for Rate Limits
- Synchronization of methods and Improve Code in many Models ( :class:`bale.User`, :class:`bale.Chat`, :class:`bale.Bot`, :class:`bale.Message` )
- Add :attr:`bale.User.chat_id`
- Add :class:`bale.error.RateLimited` Error
- Add ``sleep_after_every_get_updates`` param to :meth:`bale.Bot.run` and :meth:`bale.Bot.start`

Bug Fixes
~~~~~~~~~~

- Improve Code Quality

v2.3.2
------

New Features
~~~~~~~~~~~~
- Add new methods :meth:`bale.Bot.get_user` and :meth:`bale.Bot.invite_to_chat` function
- Support :meth:`bale.Chat.invite_to_chat` from :meth:`bale.Bot.get_user`
- Add :attr:`bale.Chat.mention` and :attr:`bale.Chat.link` property to :class:`bale.Chat`
- Add :attr:`bale.CallbackQuery.user` property to :class:`bale.CallbackQuery` .  :attr:`bale.CallbackQuery.user` is a aliases for :attr:`bale.CallbackQuery.from_user`.
- Add ``on_member_chat_join`` and ``on_member_chat_leave`` events
- Add :meth:`bale.MemberRole.is_admin` and :meth:`bale.MemberRole.is_owner` function to :class:`bale.MemberRole`
- Add `save` and `read` function to be `bale.Document`
- Add `get_file` function to `bale.HTTPClient`

Bug Fixes
~~~~~~~~~~

- Fixed some function in :class:`bale.Bot`
- Fixed ``Bad Request`` error in :meth:`bale.Bot.get_chat`
- Fixed `on_ready` event bug
- Fixed :meth:`bale.Bot.get_chat` bugs