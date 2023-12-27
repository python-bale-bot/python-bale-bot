"""
MIT License

Copyright (c) 2023 Kian Ahmadian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from typing import Optional
from bale import BaleObject

__all__ = (
    "Contact",
)

class Contact(BaleObject):
    """This object shows a Contact.

    Attributes
    ----------
        phone_number: int
            Contact’s phone number.
        first_name: str
            Contact’s first name.
        last_name: Optional[:class:`str`]
            Contact’s last name.
        user_id: Optional[:class:`int`]
            Contact’s user identifier in Bale.
    """
    __slots__ = (
        "phone_number",
        "first_name",
        "last_name",
        "user_id"
    )

    def __init__(self, phone_number: int, first_name: str, last_name: Optional[str], user_id: Optional[int]):
        super().__init__()
        self._id = user_id
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id

        self._lock()
