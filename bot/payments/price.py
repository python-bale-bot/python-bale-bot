class Price():
    __slots__ = ("label", "amount")
    def __init__(self, label : str, amount : int = None):
        self.label = label
        self.amount = amount
        
    @classmethod
    def dict(cls, data):
        return cls(label = data["label"], amount = data["amount"])
    
    def to_dic(self):
        data = {}
        
        data["label"] = self.label
        data["amount"] = self.amount
        
        return data