from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from todo_fast.database import get_session
from todo_fast.models import Todo, User
from todo_fast.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from todo_fast.security import get_current_user

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/todos', tags=['todos'])


@router.post('/', response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: Session,
):
    """
    Creates a new todo item for the authenticated user.

    This endpoint receives a `TodoSchema`
    containing the title, description,
    and state of the todo. It associates
    the new todo with the `user_id`
    of the currently authenticated user.

    Args:
        todo (TodoSchema): The Pydantic model for the todo
        item to create.
        user (CurrentUser): The authenticated user object,
        injected by `get_current_user`.
        session (Session): The database session,
        injected by `get_session`.

    Returns:
        TodoPublic: The newly created todo item,
        including its generated ID.
    """
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
async def list_todos(
    session: Session,
    user: CurrentUser,
    todo_filter: Annotated[FilterTodo, Query()]
):
    """
    Retrieves a list of todo items belonging to the authenticated user.

    This endpoint supports filtering by `title`,
    `description` (partial matches),
    and `state`. It also supports pagination using
    `offset` and `limit` query parameters.

    Args:
        session (Session): The database session,
        injected by `get_session`.
        user (CurrentUser): The authenticated user object,
        injected by `get_current_user`.
        todo_filter (FilterTodo): Query parameters for
        filtering and pagination (
            offset, limit, title, description, state).

    Returns:
        TodoList: A list of `TodoPublic` objects matching the criteria.
    """
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(
            Todo.title.contains(todo_filter.title)
        )

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(
            Todo.state == todo_filter.state
        )

    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {'todos': todos.all()}


@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(
    todo_id: int,
    session: Session,
    user: CurrentUser,
    todo: TodoUpdate
):
    """
    Partially updates an existing todo item belonging
    to the authenticated user.

    This endpoint allows updating one or more fields
    (title, description, state)
    of a specific todo item identified by `todo_id`.
    Only the authenticated user
    can update their own todo items.

    Args:
        todo_id (int): The ID of the todo item to update.
        session (Session): The database session,
        injected by `get_session`.
        user (CurrentUser): The authenticated user object
        injected by `get_current_user`.
        todo (TodoUpdate): The Pydantic model with fields to update (
            only provided fields will be changed).

    Raises:
        HTTPException (404 Not Found): If the todo item
        with the given ID is not found
                                       or does not belong to the current user.

    Returns:
        TodoPublic: The updated todo item.
    """
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(todo_id: int, session: Session, user: CurrentUser):
    """
    Deletes a specific todo item belonging to the authenticated user.

    This endpoint removes a todo item
    identified by `todo_id`. Only the
    authenticated user can delete their own todo items.

    Args:
        todo_id (int): The ID of the todo item to delete.
        session (Session): The database session, injected by `get_session`.
        user (CurrentUser): The authenticated user object,
        injected by `get_current_user`

    Raises:
        HTTPException (404 Not Found): If the todo item with the given
        ID is not found
                                       or does not belong to the current user.

    Returns:
        Message: A confirmation message indicating successful deletion.
    """
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been deleted successfully.'}
