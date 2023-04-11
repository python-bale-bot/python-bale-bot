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


class Video:
    """This object shows a Video.

    Attributes
    ----------
        file_id: str
            Video ID
        width: int
            Video width
        file_size: int
            Video Size.
        height: str
            Video height.
        duration: int
            Video duration.

    """
    __slots__ = (
        "file_id",
        "width",
        "height",
        "file_size",
        "duration"
    )

    def __init__(self, file_id: str, width: int, height: int, file_size: int, duration: int):
        self.file_id = file_id
        self.width = width
        self.height = height
        self.file_size = file_size
        self.duration = duration

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            file_id=data.get("file_id"),
            width=data.get("width"),
            height=data.get("height"),
            file_size=data.get("file_size"),
            duration=data.get("duration")
        )

    def to_dict(self):
        data = {
            "file_id": self.file_id,
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
            "duration": self.duration
        }
        return data
