class Audio:
    """This object shows a waist.

    Attributes
    ----------
        file_id: str
            Audio ID
        duration: int
            Audio duration
        file_size: int
            Audio Size.
        mime_type: Optional[:class:`str`]
            Audio Mime type.
        title: Optional[:class:`str`]
            Audio Title.
    """
    __slots__ = (
        "file_id",
        "duration",
        "title",
        "file_size",
        "mime_type",
        "bot"
    )

    def __init__(self, file_id: str, duration: int, file_size: int = None, mime_type: str = None, title: str = None):
        self.file_id = file_id
        self.duration = duration

        self.title = title
        self.file_size = file_size
        self.mime_type = mime_type

    @classmethod
    def from_dict(cls, data):
        return cls(file_id=data["file_id"], duration=data["duration"], file_size=data["file_size"], title=data["title"],
                   mime_type=data["mime_type"])

    def to_dict(self):
        data = {"file_id": self.file_id if self.file_id is not None else None,
                "duration": self.duration if self.duration is not None else None,
                "title": self.title if self.title is not None else None,
                "file_size": self.file_size if self.file_size is not None else None,
                "mime_type": self.mime_type if self.mime_type is not None else None}

        return data