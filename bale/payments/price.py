from __future__ import annotations


class Price:
    """This object shows a Price

        Args:
            label (str): Label Price. Defaults to None.
            amount (int): Amount Price. Defaults to None.
    """
    __slots__ = ("label", "amount")

    def __init__(self, label: str = None, amount: int = None):
        self.label = label
        self.amount = amount
        
    @classmethod
    def from_dict(cls, data):
        """
        Args:
            data (dict): Data
        """
        return cls(label=data["label"], amount=data["amount"])
    
    def to_dict(self):
        """Convert Class to dict
            Returns:
                :dict:
        """
        data: dict[str, int | str] = {
            "label": self.label,
            "amount": self.amount
        }
        return data
