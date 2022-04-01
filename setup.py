from setuptools import setup, find_packages
import balebot

setup(
    name = "balebot",
    version = balebot.__version__,
    platforms = ["Windows"],
    author = "Kian Ahmadian",
    license = "MIT License",
    project_urls = {
        "Source Code": "https://github.com/kianahmadian/bale-bot/"    
    },
    keywords = ["bale", "bot", "api"],
    python_requires = '>=3.8',
    url = "https://github.com/kianahmadian/bale-bot/",
    packages = find_packages()
) 

print(r"""
____    __        ____   ____  ____  _____
|___|  /__\  |    |___   |___| |   |   |
|___| /    \ |___ |___   |___| |___|   |

""")