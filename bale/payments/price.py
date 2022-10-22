from __future__ import annotations


class Price:
	"""This object shows a Price

    Attributes
    ----------
        label: Optional[:class:`str`]
            Label Price.
        amount: Optional[:class:`int`]
            Amount Price.
    """
	__slots__ = ("label", "amount")

	def __init__(self, label: str = None, amount: int = None):
		self.label = label
		self.amount = amount

	@classmethod
	def from_dict(cls, data):
		return cls(label=data["label"], amount=data["amount"])

	def to_dict(self):
		data: dict[str, int | str] = {
			"label": self.label,
			"amount": self.amount
		}
		return data
