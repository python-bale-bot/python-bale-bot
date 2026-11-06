"""
Python Bale Bot
~~~~~~~~~~~~~~~

An API wrapper for Bale written in Python.

Copyright (C) 2026. All Rights Reserved.

"""

import sys

from .version import __version__


def main() -> None:
    print("python-bale-bot by Kian Ahmadian")
    print(f"Python Version: {sys.version}")
    print(f"python-bale-bot Version: {__version__}")


if __name__ == "__main__":
    main()
