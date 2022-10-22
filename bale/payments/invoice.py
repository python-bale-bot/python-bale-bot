from __future__ import annotations


class Invoice:
	"""This object shows Invoice

    Attributes
    ----------
        title: str
        	Invoice title.
        description: str
        	Invoice Description.
        start_parameter: str
        	No Description.
        currency: str
        	No Description.
        total_amount: int
        	No Description.
    """
	__slots__ = (
		"title",
		"description",
		"start_parameter",
		"currency",
		"total_amount"
	)
	def __init__(self, title: str, description: str, start_parameter: str, currency: str, total_amount: int):
		self.title = title
		self.description = description
		self.start_parameter = start_parameter
		self.currency = currency
		self.total_amount = total_amount

	@classmethod
	def from_dict(cls, data: dict):
		return cls(
			title=data.get("title"),
			description=data.get("description"),
			start_parameter=data.get("start_parameter"),
			currency=data.get("currency"),
			total_amount=data.get("total_amount")
		)
