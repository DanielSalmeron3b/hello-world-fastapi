# Python
from typing import Optional, List # <- para tipado estático y para listas
from enum import Enum # <- para enumerar strings
# Pydantic
from pydantic import (
    BaseModel, AnyUrl, PastDate, 
    EmailStr, Field
    )
# FastAPI
from fastapi import (
    FastAPI, Body, Query, 
    Path, status, Form, 
    Header, Cookie, UploadFile, 
    File, HTTPException
    )

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

class LoginOut(BaseModel):
    username: str = Field(
        ...,
        max_length=20,
        example="salmeron_dev",
    )


@app.get(
    "/", 
    status_code=status.HTTP_200_OK,
    tags=["Home"]
    ) # <- path operation decorator
def home():
    return {"Hello": "World!"}

# Request and Response Body
# - Cómo se envía un request body a una API -

@app.post(
    path="/person/new", 
    response_model=Person,
    response_model_exclude={'password'},
    status_code=status.HTTP_201_CREATED,
    tags=["Persons"]
    )
def create_person(person: Person = Body(...)):
    return person

# Validations: Query Parameters

@app.get(
    path="/person/detail",
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
    )
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

persons = [1, 2, 3, 4, 5]

@app.get(
    path="/person/detail/{person_id}",
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
    )
def show_person(
    person_id: int = Path(
        ...,
        gt=0,
        title="Person Id",
        description="This is the person id.",
        example=123
        )
):
    if person_id not in persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This person does not exist :("
        )
    
    return {person_id: "This person exists!"}

# Validations: Request Body

@app.put(
    path="/person/{person_id}",
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
    )
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

# Forms

@app.post(
    path="/login",
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
)
def login(
    username: str = Form(...),
    password: str = Form(...),
):
    return LoginOut(username=username)

# Cookies and Headers Parameters

@app.post(
    path="/contact",
    status_code=status.HTTP_200_OK,
    tags=["Contact"]
)
def contact(
    first_name: str = Form(
        ...,
        max_length=20,
        min_length=1,
    ),
    last_name: str = Form(
        ...,
        max_length=20,
        min_length=1,
    ),
    email: EmailStr = Form(...),
    message: str = Form(
        ...,
        min_length=20,
        max_length=400,
    ),
    # Headers
    user_agent: Optional[str] = Header(default=None),
    # Cookies
    ads: Optional[str] = Cookie(default=None),
):
    return user_agent

# Files
@app.post(
    path="/post-image",
    tags=["UploadFile"]
)
def post_image(
    images: List[UploadFile] = File(...),
):
    # List comprehension to upload multiple files
    info_images = [{
        "filename": image.filename,
        "Format": image.content_type,
        "Size(kb)": round(len(image.file.read())/1024, ndigits=2)
    } for image in images ]

    return info_images