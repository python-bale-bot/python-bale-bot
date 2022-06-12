class Document:
    """This object shows a Document.

        Args:
            file_id (str): Defaults to None.
            file_name (str): Defaults to None.
            mime_type (str): Defaults to None.
            file_size (int): Defaults to None.
    """
    __slots__ = (
        "file_id",
        "file_name",
        "mime_type",
        "file_size"
    )

    def __init__(self, file_id: str = None, file_name: str = None, mime_type: str = None, file_size: int = None):
        self.file_id = file_id if file_id is not None else None
        self.file_name = file_name if file_name is not None else None
        self.mime_type = mime_type if mime_type is not None else None
        self.file_size = file_size if file_size is not None else None

    @classmethod
    def from_dict(cls, data: dict):
        """
        Args:
            data (dict): Data
        """
        return cls(file_id=data.get("file_id"), file_name=data.get("file_name"),
                   mime_type=data.get("mime_type"), file_size=data.get("file_size"))

    def to_dict(self):
        data = {"file_id": self.file_id, "file_name": self.file_name, "mime_type": self.mime_type, "file_size": self.file_size}

        return data
