.. currentmodule::bale

Change Log
==========

Project changes are shown on this page.

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