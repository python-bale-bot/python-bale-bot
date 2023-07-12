class InputFile:
    __slots__ = (
        "file_type",
        "name",
        "content"
    )
    def __init__(self, file_type, name, content):
        self.file_type = file_type
        self.name = name
        self.content = content

    def to_dict(self):
        return {
            "name": self.file_type,
            "value": self.content,
            "filename": self.name
        }

    def __eq__(self, other):
        return isinstance(other, InputFile) and self.content == other.content

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<InputFile name={self.name} filetype={self.file_type} >"
