from fastapi import FastAPI, Depends, HTTPException
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

app = FastAPI(lifespan = life_span, title="Hello World API with DB",)

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

@app.put("/todo/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: Todo, session: Annotated[Session, Depends(get_session)]):
    select_todo = select(Todo).where(Todo.id == todo_id)
    selected_todo = session.exec(select_todo).first()
    # selected_todo = session.exec(select(Todo).where(Todo.id == todo_id)).first()
    if not selected_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    selected_todo.status = todo.status
    session.commit()
    session.refresh(selected_todo)
    return selected_todo

@app.delete("/todo/{todo_id}", response_model=Todo)
def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    selected_todo = session.exec(select(Todo).where(Todo.id == todo_id)).first()
    if not selected_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(selected_todo)
    session.commit()
    return selected_todo
