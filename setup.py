from setuptools import setup, find_packages

setup(
    name = "python-bale-bot",
    version = "2.2.1",
    platforms = ["Windows"],
    author = "kianahmadian",
    license = "MIT License",
    project_urls = {
        "Source Code": "https://github.com/kianahmadian/bale-bot/"    
    },
    keywords = ["bale", "bot", "api"],
    python_requires = '>=3.8',
    include_package_data=True,
    url = "https://github.com/kianahmadian/bale-bot/",
    packages = ['balebot'],
    package_dir = "",
    install_requires = [
"aiohttp==2.3.7",
"async-timeout==2.0.0",
"asyncio==3.4.3",
"requests=>2.26.0"]
) 

print(r"""
____    __        ____   ____  ____  _____
|___|  /__\  |    |___   |___| |   |   |
|___| /    \ |___ |___   |___| |___|   |

""")