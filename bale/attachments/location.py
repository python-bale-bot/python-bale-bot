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
from __future__ import annotations
from typing import Optional
from bale import BaleObject

__all__ = (
    "Location",
)

class Location(BaleObject):
    """This object shows a Location

    Attributes
    ----------
        longitude: :class:`int`
            Location longitude
        latitude: :class:`int`
            Location latitude
        horizontal_accuracy: Optional[:class:`int`]
            The radius of uncertainty for the location, measured in meters; 0-1500.
    """
    __slots__ = (
        "longitude",
        "latitude",
        "horizontal_accuracy"
    )

    def __init__(self, longitude: int, latitude: int, horizontal_accuracy: Optional[int] = None):
        super().__init__()
        self.longitude = longitude
        self.latitude = latitude
        self.horizontal_accuracy = horizontal_accuracy
        self._id = (longitude, latitude, horizontal_accuracy)

        self._lock()

    @property
    def link(self) -> str:
        """:class:`str`: Export location link from Google map"""
        return f"https://maps.google.com/maps?q=loc:{self.longitude},{self.latitude}"

