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


class Location:
    """This object shows an end

    Attributes
    ----------
        longitude: int
            Location longitude
        latitude: int
            Location latitude
    """
    __slots__ = (
        "longitude",
        "latitude"
    )

    def __init__(self, longitude: int, latitude: int):
        self.longitude = longitude
        self.latitude = latitude

    @property
    def link(self) -> str:
        """:class:`str`: export location link from map"""
        return f"https://maps.google.com/maps?q=loc:{self.longitude},{self.latitude}"

    @classmethod
    def from_dict(cls, data):
        return cls(longitude=data["longitude"], latitude=data["latitude"])

    def to_dict(self):
        data = {"longitude": self.longitude if self.longitude is not None else None,
                "latitude": self.latitude if self.latitude is not None else None}
        return data

    def __eq__(self, other):
        return isinstance(other, Location) and self.link == other.link

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<Location longitude={self.longitude} latitude={self.latitude} >"
