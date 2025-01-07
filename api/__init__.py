from typing import List
import azure.functions as func
import os
from fastapi import FastAPI

from api.ingredient import Ingredient
from api.ingredient_parser import parse_ingredients_crf

fastapi_app = FastAPI()

# Define the path to the CRF model relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE_PATH = os.path.join(SCRIPT_DIR, "models/model-0601.crfmodel")

@fastapi_app.get("/")
async def read_root():
    return {"Hello": "World"}

@fastapi_app.put("/ingredients")
async def parse_ingredients_endpoint(ingredients: List[Ingredient]):
    parsed_responses = []  # List to store individual parsed responses
        
    for ingredient in ingredients:
        # Convert the ingredient to a string
        sentence = str(ingredient)
        
        # Parse the ingredient using the CRF model
        parsed_response = parse_ingredients_crf([sentence], MODEL_FILE_PATH)  # Pass the single ingredient in a list
        
        # Append the parsed response to the list
        parsed_responses.append(parsed_response)
    
    return parsed_responses

app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)