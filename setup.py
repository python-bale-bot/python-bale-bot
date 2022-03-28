from setuptools import setup
import balebot

with open("./README.md") as file:
    readmefile = file.read()
setup(
    name = "balebot",
    version = balebot.__version__,
    platforms = ["Windows"],
    author = "Kian Ahmadian",
    zip_safe = True,
    long_description = readmefile,
    long_description_content_type = 'text/markdown',
    keywords = ["bale", "bot", "api"]
) 

print(r"""
____    __        ____   ____  ____  _____
|___|  /__\  |    |___   |___| |   |   |
|___| /    \ |___ |___   |___| |___|   |

""")