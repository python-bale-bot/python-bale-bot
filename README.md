# python-bale-bot Library

<div align='center'>
<img width="600" src="https://python-bale-bot.ir/assets/images/banner.png" alt="python-bale-bot image">
<br>
<b style='margin-bottom:50px;'>An API wrapper for Bale written in Python. </b>
<br>

[![Python Version](https://img.shields.io/badge/Python-3.8_|_3.9_|_3.10_|_3.11_|_3.12_-red?logo=python&style=plastic)](https://python.org)
[![PyPi Version](https://img.shields.io/pypi/v/python-bale-bot?color=blue&label=pypi&style=plastic&logo=pypi)](https://pypi.org/p/python-bale-bot)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/deacf2bc3f13492d944e329ac19ac0d1)](https://www.codacy.com/gh/python-bale-bot/python-bale-bot/dashboard)
[![python-bale-bot score](https://snyk.io/advisor/python/python-bale-bot/badge.svg)](https://snyk.io/advisor/python/python-bale-bot)
[![Project License](https://img.shields.io/github/license/python-bale-bot/python-bale-bot?style=plastic)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![API Version](https://img.shields.io/badge/Bale%20API-2.0-blue?style=plastic)](https://docs.bale.ai)
[![Documentation Status](https://readthedocs.org/projects/python-bale-bot/badge/?version=stable)](https://docs.python-bale-bot.ir/)

</div>

# Introduction

## What is Bale?
**The "Bale" is a messenger-platform for send and receive messages.** it's provides services for developers, and they can send or receive messages through `bots` like normal users and These services are provided by [web services](https://dev.bale.ai) (`API`).

## What is python-bale-bot?
**The "python-bale-bot" is a Python language package optimized for developers to use web services provided by "Bale".**

# Installing
<div align='center'>
  
  **You can install or update `python-bale-bot` via:**
  
</div>

### PyPi:

```
$ pip install python-bale-bot -U
```

### Git:

```
$ git clone https://github.com/python-bale-bot/python-bale-bot
$ cd python-bale-bot
$ python setup.py install
```

# Quick Start
To get started, learn how the library works through the library. In addition, there are examples in the "[Examples](https://docs.python-bale-bot.ir/en/stable/examples.html)" section of the library.

```python
from bale import Bot, Message
from bale.handlers import CommandHandler

client = Bot(token="YOUR TOKEN")

@client.event
async def on_ready():
	print(client.user, "is Ready!")

@client.handle(CommandHandler("start"))
async def on_message(message: Message):
	await message.reply(f'Hi {message.author.first_name}!')

client.run()
```

# Documentation
**The [package documentation](https://docs.python-bale-bot.ir/en/stable) is the technical reference for python-bale-bot. It contains descriptions of all available classes, modules, methods and arguments as well as the changelog.**


# Contact to Developers
[![Email](https://img.shields.io/badge/Email-python--bale--bot@googlegroups.com-green?logo=Gmail&logoColor=white)](mailto:python-bale-bot@googlegroups.com)
[![Discord](https://img.shields.io/discord/942347256508596225?logo=discord&logoColor=white&label=Support%20Server
)](https://discord.gg/bYHEzyDe2j)
[![Telegram Channel](https://img.shields.io/badge/Telegram_Channel-@pbblib-green?logo=telegram&logoColor=white)](https://t.me/pbblib)
[![Our Site](https://img.shields.io/badge/Our_site-python--bale--bot.ir-green?logo=GitHub&logoColor=white)](https://python-bale-bot.ir)
