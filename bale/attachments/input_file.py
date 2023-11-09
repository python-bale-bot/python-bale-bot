from __future__ import annotations

from typing import Optional, Dict
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
        file: :class:`io.BufferedReader` | :class:`str` | :class:`bytes`
            Your File. Pass a file_id as String to send a file that exists on the Bale servers (recommended), pass an HTTP URL as a String for Bale to get a file from the Internet, or upload a new one.
        file_name: Optional[:class:`str`]
            Additional interface options. It is used only when uploading a file.
    """
    PHOTO_TYPE = "photo"
    ANIMATION_TYPE = "animation"
    VIDEO_TYPE = "video"
    DOCUMENT_TYPE = "document"
    AUDIO_TYPE = "audio"
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

    def to_multipart_payload(self, media_type: str) -> Dict:
        payload = {
            "value": self.file,
            "name": media_type
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
