from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from todo_fast.schemas import (
    Message,
    UserDB,
    UserList,
    UserPublic,
    UserSchemas,
)

database = []

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    """
    GET/

    Returns a welcome message for the API root endpoint.
    """
    return {'message': 'Hello, World!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchemas):
    """
    Create a new user.

    Receives user data (username, email, password), assings a unique ID,
    stores it in the in-memory database, and returns the created user
    without expossing the password.
    """
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)

    database.append(user_with_id)

    return user_with_id


@app.get('/users/', response_model=UserList)
def read_users():
    """
    Retrieve all users.

    Returns a list of users currently stored in the database.
    """
    return {'users': database}


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchemas):
    """
    Update an existing user.

    Updates the username, email, password of the user specified
    by user_id. Raises 404 if the user does not exist.
    """
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    """
    Delete a user.

    Removes the user specified by user_id from the database.
    Raises 404 if the user does not exist.
    """
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]

    return {'message': 'User deleted'}
