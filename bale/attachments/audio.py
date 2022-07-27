class Audio:
    __slots__ = (
        "file_id",
        "duration",
        "title",
        "file_size",
        "mime_type",
        "bot"
    )

    def __init__(self, file_id: id, duration: int, file_size: int = None, mime_type: str = None, title: str = None):
        """This object shows a waist

        Args:
            file_id (id): Audio ID
            duration (int): Audio duration
            file_size (int): Audio Size. Defaults to None.
            mime_type (str): Audio Mime type. Defaults to None.
            title (str): Audio Title. Defaults to None.
        """
        self.file_id = file_id
        self.duration = duration

        self.title = title
        self.file_size = file_size
        self.mime_type = mime_type

    @classmethod
    def from_dict(cls, data):
        """
        Args:
            data (dict): Data
        """
        return cls(file_id=data["file_id"], duration=data["duration"], file_size=data["file_size"], title=data["title"],
                   mime_type=data["mime_type"])

    def to_dict(self):
        data = {"file_id": self.file_id if self.file_id is not None else None,
                "duration": self.duration if self.duration is not None else None,
                "title": self.title if self.title is not None else None,
                "file_size": self.file_size if self.file_size is not None else None,
                "mime_type": self.mime_type if self.mime_type is not None else None}

        return data

    def get_file(self):
        # Coming Soon...
        pass
