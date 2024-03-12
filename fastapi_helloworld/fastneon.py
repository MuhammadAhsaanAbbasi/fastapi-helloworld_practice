from fastapi import FastAPI, Depends, Query
from sqlmodel import SQLModel, Session, create_engine, select, Field
from fastapi_helloworld import settings
from contextlib import asynccontextmanager
from typing import Optional, Annotated

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True,)
    todo: str = Field(index=True)
    status: bool = Field(default=False)


connectionString = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg")

engine = create_engine(connectionString, connect_args={"sslmode": "require"}, pool_recycle=500)

def db_create_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Creating Tables...")
    db_create_and_tables()
    yield 

app = FastAPI(lifespan = life_span, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://0.0.0.0:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
def get_root():
    return {"Message": "Hello World"}

@app.post("/todo/", response_model=Todo)
def get_todos(todo: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get("/todo/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos
