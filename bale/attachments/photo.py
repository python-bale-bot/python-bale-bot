class Photo:
	__slots__ = (
		"file_id",
		"width",
		"height",
		"file_size"
	)
	def __init__(self, file_id: str, width: int, height: int, file_size: int):
		self.file_id = file_id
		self.width = width
		self.height = height
		self.file_size = file_size

	@classmethod
	def from_dict(cls, data: dict):
		return cls(
			file_id=data.get("file_id"),
			width=data.get("width"),
			height=data.get("height"),
			file_size=data.get("file_size")
		)

	def to_dict(self):
		data = {
			"file_id": self.file_id,
			"width": self.width,
			"height": self.height,
			"file_size": self.file_size
		}
		return data