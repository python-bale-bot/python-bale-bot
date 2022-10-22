from setuptools import setup, find_packages

def get_readme_file() -> str:
    """Get Readme File"""
    with open("README.md", encoding="utf-8") as f:
        readme_file = f.read()
    return readme_file

extras_require = {
    'docs': [
        'sphinx==4.4.0',
        'sphinxcontrib_trio==1.1.2',
        'sphinxcontrib-websupport',
        'typing-extensions>=4.3,<5',
    ],
}

if __name__ == "__main__":
    setup(
        name="python-bale-bot",
        version="2.3.2",
        platforms=["Windows"],
        fullname="python-bale-bot",
        description="An API wrapper for Bale written in Python",
        author="Kian Ahmadian",
        license="MIT License",
        project_urls={
            "Source Code": "https://github.com/kian-ahmadian/python-bale-bot/",
            "Documentation": "https://python-bale-bot.readthedocs.io/en/latest/",
            "Bug Tracker": "https://github.com/kian-ahmadian/python-bale-bot/issues"
        },
        keywords=["bale", "bale-bot", "framework"],
        python_requires='>=3.8',
        extras_require=extras_require,
        include_package_data=True,
        url="https://github.com/kian-ahmadian/python-bale-bot/",
        packages=find_packages(),
        long_description=get_readme_file(),
        long_description_content_type='text/markdown',
        install_requires=["aiohttp<3.8.0,>=3.6.0", "asyncio~=3.4.3", "setuptools~=60.2.0"]
    )



print(r"""
____    __        ____   ____  ____  _____
|___|  /__\  |    |___   |___| |   |   |
|___| /    \ |___ |___   |___| |___|   |

""")
