from setuptools import setup
import balebot

with open("README.md") as file:
    readmefile = file.read()
setup(
    name = "balebot",
    version = balebot.__version__,
    platforms = ["Windows"],
    author = "Kian Ahmadian",
    long_description = readmefile,
    keywords = ["bale", "bot", "api"]
) 

print(r"""
____    __        ____   ____  ____  _____
|___|  /__\  |    |___   |___| |   |   |
|___| /    \ |___ |___   |___| |___|   |

""")