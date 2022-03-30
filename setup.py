from setuptools import setup
import balebot

setup(
    name = "balebot",
    version = balebot.__version__,
    platforms = ["Windows"],
    author = "Kian Ahmadian",
    keywords = ["bale", "bot", "api"],
    python_requires='>=3.5',
    requires = ["requests"],
    url = "https://github.com/kianahmadian/bale-bot",
    packages = ['balebot']
) 

print(r"""
____    __        ____   ____  ____  _____
|___|  /__\  |    |___   |___| |   |   |
|___| /    \ |___ |___   |___| |___|   |

""")