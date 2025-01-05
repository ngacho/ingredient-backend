from typing import Union, List, Optional
from fastapi import FastAPI
from ingredient_parser import parse_multiple_ingredients
from ingredient_parser.dataclasses import ParsedIngredient
from pydantic import BaseModel

app = FastAPI()

# Input Model
class Ingredient(BaseModel):
    name: str
    amount: str
    unit: str

    def __str__(self):
        return f"{self.amount} {self.unit} {self.name}"

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.put("/ingredients")
async def parse_ingredients(ingredients: List[Ingredient]):

    sentences = [str(ingredient) for ingredient in ingredients]

    parsed_response = parse_multiple_ingredients(sentences)
    
    return parsed_response
