from balebot import *
from time import sleep

class BaleApp(Bot):
    def __init__(self):
        offset = None
        bot = Bot.__init__(self, base_url="https://tapi.bale.ai/", token = "634737971:xGwkvAEjSN4vX7UBnCFhlgJcEABYfZa7xst2By7m", base_file_url = "s", prefix = "-")
        while True:
            updates = self.get_updates(timeout = (10,30), offset = offset)
            for i in updates:
                i = Update(i.json, i.base_class)
                if offset:
                    if offset >= i.id:
                        continue
                if i.type == "callback_query":
                    if i.callback_query.data == "help":
                        i.callback_query.message.reply(text = "salam", components = ReplyMarkup(keyboards=[]))
                    elif i.callback_query.data == "test":
                        i.callback_query.message.delete((10, 30))
                elif i.type == "message":
                    if i.message.text == "test":
                        i.message.reply(text = f"salam {i.message.author}", components = ReplyMarkup(inlinekeyboards = [[InlineKeyboard("salam", "help")]]))
            if updates != [] or updates:
                offset = updates[-1].id
            sleep(6.0)
BaleApp()