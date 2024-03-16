from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from fastapi_helloworld import settings
from sqlmodel import Session, SQLModel, create_engine, select
from fastapi import FastAPI, Query, Path, Body


# class Todo(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     content: str = Field(index=True)


# # only needed for psycopg 3 - replace postgresql
# # with postgresql+psycopg in settings.DATABASE_URL
# connection_string = str(settings.DATABASE_URL).replace(
#     "postgresql", "postgresql+psycopg"
# )


# # recycle connections after 5 minutes
# # to correspond with the compute scale down
# engine = create_engine(
#     connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
# )


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Creating tables..")
#     create_db_and_tables()
#     yield


app = FastAPI(title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://0.0.0.0:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

# def get_session():
#     with Session(engine) as session:
#         yield session


@app.get("/")
def read_root():
    return {"Message": "Hello World"}

# @app.post("/todos/", response_model=Todo)
# def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
#         session.add(todo)
#         session.commit()
#         session.refresh(todo)
#         return todo


# @app.get("/todos/", response_model=list[Todo])
# def read_todos(session: Annotated[Session, Depends(get_session)]):
#         todos = session.exec(select(Todo)).all()
#         return todos

# Additional Validation 
from typing import Annotated

# @app.get("/items/")
# async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
#     results: dict[str, Union[str, list[dict[str, str]]]] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

# @app.get("/items/")
# async def read_items(q: str | None = Query(default="rick", max_length=50, min_length=3, regex="^fixedquery$")):
#     results: dict[str, Union[str, list[dict[str, str]]]] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
    ] = None,
):
    results: dict[str, Union[str, list[dict[str, str]]]] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.get("/item/")
async def read_item(
    hidden_query: Annotated[str | None, Query(include_in_schema=False)] = None
):
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not found"}

@app.get("/items/{item_id}")
async def read_items_id(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=1, le=1000)],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results: dict[str, Union[str, int]] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# from pydantic import BaseModel

# class Item(BaseModel):
#     name: str
#     description: str | None = None
#     price: float
#     tax: float | None = None


# class User(BaseModel):
#     username: str
#     full_name: str | None = None


# # @app.put("/items/{item_id}")
# # async def update_item(item_id: int, item: Item, user: User, importance: Annotated[int, Body()]):
# #     results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
# #     return results

# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
#     results = {"item_id": item_id, "item": item}
#     return results

from pydantic import BaseModel, Field


# class Item(BaseModel):
#     name: str
#     description: str | None = Field(
#         default=None, title="The description of the item", max_length=200
#     )
#     price: float = Field(gt=0, description="The price must be greater than zero")
#     tax: float | None = None


# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
#     results = {"item_id": item_id, "item": item}
#     return results

from pydantic import HttpUrl


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: list[Image] | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

import json
import jsonschema as jsonschema
@app.get("/json")
def get_json(name: str, age: int):
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 18},
        },
        "required": ["name", "age"],
    }
    data = {"name": name, "age": age}
    try:
        jsonschema.validate(instance=data, schema=schema)
        return {"message": "data valid!"}
    except jsonschema.exceptions.ValidationError as e:
        return {"message": str(e)}

