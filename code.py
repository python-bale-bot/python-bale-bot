from balebot import *
from time import sleep

class BaleApp(Bot):
    def __init__(self):
        offset = 2
        bot = Bot.__init__(self, base_url="https://tapi.bale.ai/", token = "634737971:xGwkvAEjSN4vX7UBnCFhlgJcEABYfZa7xst2By7m", base_file_url = "s", prefix = "-")
        updates = self.get_updates(timeout = (10,30), offset = offset)
        for i in updates:
            if i.type == "callback_query":
                i.callback_query.message.reply(text = f"{i.callback_query.data} click shod!")
            elif i.type == "message":
                i.message.reply(text = f"salam {i.message.author.mention}", components = ReplyMarkup(inlinekeyboards = [[InlineKeyboard("salam", "ss")]]))
BaleApp()