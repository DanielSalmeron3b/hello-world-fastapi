# Python
from doctest import Example
from typing import Optional # <- para tipado estático
from enum import Enum
from urllib import response # <- para enumerar strings
# Pydantic
from pydantic import BaseModel, AnyUrl, PastDate, EmailStr, Field
# FastAPI
from fastapi import FastAPI, Body, Query, Path

app = FastAPI()

# Models

class HairColor(Enum):
    white = "white"
    brown = "brown"
    black = "black"
    blonde = "blonde"
    redhead = "redhead"

class Location(BaseModel):
    city: str = Field(
        ...,
        min_length=1,
        max_length=86,
        )
    state: str = Field(
        ...,
        min_length=1,
        max_length=86,
    )
    country: str = Field(
        ...,
        min_length=4,
        max_length=56,
    )
    
    class Config:
        schema_extra = {
            "example": {
                "city": "Detroit",
                "state": "Michigan",
                "country": "USA",
            }
        }

class Person(BaseModel):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="Daniel"
        )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="Salmeron"
        )
    age: int = Field(
        ...,
        gt=0,
        le=115,
        example=19
    )
    hair_color: Optional[HairColor] = Field(
        default=None,
        example=HairColor.black,
        )
    is_married: Optional[bool] = Field(
        default=None,
        example=False
        )
    # Exotic values
    personal_website: Optional[AnyUrl] = Field(
        default=None,
        example="https://www.google.com/"
        )
    date_of_birth: PastDate = Field(
        ...,
        example="2000-01-01"
        )
    email: EmailStr = Field(
        ...,
        example="mail@salmeron.com"
        )
    password: str = Field(
        ...,
        min_length=8,
        example="12345678"
        )

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "first_name": "Daniel",
    #             "last_name": "Salmerón Alvarado",
    #             "age": 19,
    #             "hair_color": "black",
    #             "is_married": False,
    #             "personal_website": "https://google.com/",
    #             "date_of_birth": "2000-01-01",
    #             "email": "mail@salmeron.com",
    #         }
    #     }


@app.get("/") # <- path operation decorator
def home():
    return {"Hello": "World!"}

# Request and Response Body
# - Cómo se envía un request body a una API -

@app.post(
    "/person/new", 
    response_model=Person,
    response_model_exclude={'password'})
def create_person(person: Person = Body(...)):
    return person

# Validations: Query Parameters

@app.get("/person/detail")
def show_person(
    name: Optional[str] = Query(
        None, 
        min_length=1, 
        max_length=50,
        title="Person Name",
        description="This is the person name.",
        example="Marcel"
        ),
    age: int = Query(
        ...,
        title="Person Age",
        description="This is the age of the person. Required",
        example=21
        )
):
    return {name: age}

# Validations: Path Parameters

@app.get("/person/detail/{person_id}")
def show_person(
    person_id: int = Path(
        ...,
        gt=0,
        title="Person Id",
        description="This is the person id.",
        example=123
        )
):
    return {person_id: "This person exists!"}

# Validations: Request Body

@app.put("/person/{person_id}")
def update_person(
    person_id: int = Path(
        ...,
        gt=0,
        title="Person Id",
        description="This is the person id.",
        example=123
    ),
    person: Person = Body(...),
    location: Location = Body(...),
):
    results = dict(person)
    results.update(dict(location))
    return results