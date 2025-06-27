import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI

from todo_fast.routers import auth, todos, users
from todo_fast.schemas import Message

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    """
    GET /

    Returns a welcome message for the API root endpoint.
    This endpoint serves as a basic health check and introduction to the API.

    Returns:
        Message: A dictionary containing a welcome message.
    """
    return {'message': 'Hello, World!'}
