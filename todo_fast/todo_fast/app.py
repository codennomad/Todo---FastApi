from http import HTTPStatus

from fastapi import FastAPI

from todo_fast.routers import auth, users
from todo_fast.schemas import Message

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    """
    GET/

    Returns a welcome message for the API root endpoint.
    """
    return {'message': 'Hello, World!'}
