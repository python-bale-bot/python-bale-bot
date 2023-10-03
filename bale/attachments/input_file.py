from __future__ import annotations

from typing import Optional, Dict
from io import BufferedReader

class InputFile:
    """This object shows a file ready to send/upload.

    .. warning::
        To upload a file, you must fill in the "file_name" param and end it with the file extension.

    Parameters
    ----------
        file: :class:`io.BufferedReader` | :class:`str` | :class:`bytes`
            Your File. Pass a file_id as String to send a file that exists on the Bale servers (recommended), pass an HTTP URL as a String for Bale to get a file from the Internet, or upload a new one.
        file_name: Optional[:class:`str`]
            Additional interface options. It is used only when uploading a file.
    """
    __slots__ = (
        "file",
        "file_name"
    )
    def __init__(self, file: str | "BufferedReader" | bytes, *, file_name: Optional[str] = None):
        if not isinstance(file, (str, BufferedReader, bytes)):
            raise TypeError(
                "file param must be type of str, BufferedReader and bytes"
            )
        if file_name:
            if not isinstance(file_name, str):
                raise TypeError(
                    "file_name param must be type of str"
                )
            if isinstance(file, str):
                raise TypeError(
                    "You can only enter the file name when you are uploading the file"
                )

        if isinstance(file, BufferedReader):
            file = file.read()

        self.file: bytes | str = file
        self.file_name: Optional[str] = file_name

    def to_dict(self, param: str) -> Dict:
        payload = {
            "value": self.file,
            "name": param
        }
        if self.file_name:
            payload["filename"] = self.file_name

        return payload

    def __eq__(self, other) -> bool:
        return isinstance(other, InputFile) and self.file == other.file

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<InputFile file_name={self.file_name}>"
