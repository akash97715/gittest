from typing import Union

from fastapi import FastAPI
import os
from seckey import openaikey
from pydantic import BaseModel
from langchain.llms import OpenAI
import json
os.environ['OPENAI_API_KEY'] = openaikey


db_up=[]
class Query(BaseModel):
    qr: str

app = FastAPI(app='akashapp')


@app.get("/star")
def read_root():
    return {"Hello": "World"}


class Query(BaseModel):
    query: str


@app.post("/items/{query}")
def read_item(request: Query):
    llm = OpenAI(temperature=0.1)
    name = llm.predict(request.query)
    db_up.append(json.dumps(name))
    db_up.append(json.dumps(request.query))

    return {"name": name,"db":db_up}

print(db_up)
