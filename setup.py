from setuptools import setup, find_packages

def get_readme_file() -> str:
    with open("README.rst", encoding="utf-8") as f:
        readme_file = f.read()
    return readme_file

extras_require = {
    'docs': [
        'sphinx==7.2.6',
        'sphinx-pypi-upload',
        'sphinx-paramlinks==0.6.0',
        'sphinxcontrib-mermaid==0.8.1',
        'sphinx-copybutton==0.5.2',
        'furo==2023.9.10',
        'sphinx-inline-tabs==2023.4.21'
    ]
}

if __name__ == "__main__":
    setup(
        name="python-bale-bot",
        version="2.5.0",
        platforms=["Windows"],
        fullname="python-bale-bot",
        description="An API wrapper for Bale written in Python",
        author="Kian Ahmadian",
        author_email="devs@python-bale-bot.ir",
        license="LGPLv2",
        project_urls={
            "Documentation": "https://docs.python-bale-bot.ir/en/stable/",
            "Changelog": "https://python-bale-bot.ir/changelog",
            "Bug Tracker": "https://github.com/python-bale-bot/python-bale-bot/issues",
            "Source Code": "https://github.com/python-bale-bot/python-bale-bot/",
            "News": "https://t.me/pbblib"
        },
        download_url=f"https://pypi.org/project/python-bale-bot/",
        keywords="bale bale-bot framework bot",
        python_requires='>=3.8',
        extras_require=extras_require,
        include_package_data=True,
        url="https://github.com/python-bale-bot/python-bale-bot/",
        packages=find_packages(),
        long_description=get_readme_file(),
        long_description_content_type='text/x-rst',
        install_requires=["aiohttp>=3.6.0,<3.9.2", "asyncio~=3.4.3", "setuptools~=69.0.3"]
    )



print(r"""
____    __        ____   ____  ____  _____
|___|  /__\  |    |___   |___| |   |   |
|___| /    \ |___ |___   |___| |___|   |

""")
