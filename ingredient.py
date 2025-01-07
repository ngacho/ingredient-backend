from pydantic import BaseModel

class Ingredient(BaseModel):
    name: str
    amount: str
    unit: str

    def __str__(self):
        return f"{self.amount} {self.unit} {self.name}"