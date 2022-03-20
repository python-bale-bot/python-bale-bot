from balebot import *
from time import sleep

class BaleApp(Bot):
    def __init__(self):
        offset = 2
        bot = Bot.__init__(self, base_url="https://tapi.bale.ai/", token = "1705600104:blTu9Ti8GK4Lv6rLvpnegORBTVpgYgbdPFa21WlY", base_file_url = "s", prefix = "-")
        updates = self.get_updates(timeout = (10,30), offset = offset)
        for i in updates:
            print(i.message.author.username , " " , i.message.text) 
BaleApp()