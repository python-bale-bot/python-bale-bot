from __future__ import annotations

from typing import Union, Optional, Dict
from io import BufferedReader

__all__ = (
    "InputFile",
)

class InputFile:
    """This object shows a file ready to send/upload.

    .. warning::
        Just for upload file, you can use "file_name" param.
    .. admonition:: Examples

        :any:`Attachment Bot <examples.attachment>`

    .. code:: python

        # upload the file
        with open('./my_file.png', 'rb') as f:
            file = InputFile(f.read())

        # use the unique file id
        file = InputFile("YOUR_FILE_ID")

    Parameters
    ----------
        file_input: :class:`io.BufferedReader` | :obj:`str` | :class:`bytes`
            Your File. Pass a file_id as String to send a file that exists on the Bale servers (recommended), pass an HTTP URL as a String for Bale to get a file from the Internet, or upload a new one.
        file_name: :obj:`str`, optional
            Additional interface options. It is used only when uploading a file.
    """
    __slots__ = (
        "file_input",
        "file_name"
    )
    def __init__(self, file_input: str | "BufferedReader" | bytes, *, file_name: Optional[str] = None):
        if not isinstance(file_input, (str, BufferedReader, bytes)):
            raise TypeError(
                "file_input parameter must be one of str, BufferedReader, and byte types"
            )

        if isinstance(file_input, str):
            file_input = file_input.encode("utf-8")
        elif isinstance(file_input, BufferedReader):
            file_input = file_input.read()

        if file_name:
            if not isinstance(file_name, str):
                raise TypeError(
                    "file_name param must be type of str"
                )

        self.file_input: Union[bytes, str] = file_input
        self.file_name: Optional[str] = file_name

    def to_multipart_payload(self) -> Dict:
        payload = {
            "value": self.file_input,
            "content_type" : "multipart/form-data"
        }
        if self.file_name:
            payload["filename"] = self.file_name

        return payload

    def __eq__(self, other) -> bool:
        return isinstance(other, InputFile) and self.file_input == other.file_input

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<InputFile file_name={self.file_name}>"
