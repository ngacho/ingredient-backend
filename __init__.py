import azure.functions as func
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from ingredient import Ingredient
from ingredient_parser import parse_ingredients_crf

fastapi_app = FastAPI()

# Define the path to the CRF model relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE_PATH = os.path.join(SCRIPT_DIR, "models/model.crfmodel")

@fastapi_app.get("/")
async def read_root():
    return {"Hello": "World"}

@fastapi_app.put("/v2/ingredients")
async def parse_ingredients_endpoint(ingredients: List[Ingredient]):
    # Convert ingredients to strings
    sentences = [str(ingredient) for ingredient in ingredients]
    # Parse ingredients using the CRF model
    parsed_response = parse_ingredients_crf(sentences, MODEL_FILE_PATH)
    
    return parsed_response

@fastapi_app.put("/v2/iteration/ingredients")
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

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await func.AsgiMiddleware(fastapi_app).handle_async(req, context)

