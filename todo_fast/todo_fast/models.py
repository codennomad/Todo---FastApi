from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


class TodoState(str, Enum):
    """
    Enum representing the possible states of a Todo item.

    Each member corresponds to a distinct phase in the lifecycle of a todo:
    - `draft`: The initial, unconfirmed state.
    - `todo`: The item is planned but not yet started.
    - `doing`: The item is currently in progress.
    - `done`: The item has been completed.
    - `trash`: The item has been discarded or moved to trash.
    """
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


@table_registry.mapped_as_dataclass
class User:
    """
    SQLAlchemy declarative model for the 'users' table.

    Represents a user in the application, storing their authentication
    and profile information.

    Attributes:
        id (int): Primary key, automatically generated.
        username (str): Unique username for the user.
        password (str): Hashed password of the user.
        email (str): Unique email address of the user.
        created_at (datetime): Timestamp of when the user account was created,
                               defaults to the current server time.
        todos (list[Todo]): A list of Todo items associated with this user
                            (one-to-many relationship).
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    todos: Mapped[list['Todo']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )


@table_registry.mapped_as_dataclass
class Todo:
    """
    SQLAlchemy declarative model for the 'todos' table.

    Represents a single todo item, linked to a specific user.

    Attributes:
        id (int): Primary key, automatically generated.
        title (str): The title of the todo item.
        description (str): A detailed description of the todo item.
        state (TodoState): The current state of the todo item,
        chosen from `TodoState` enum.
        user_id (int): Foreign key linking to the `id` of the associated User.
        user (User): The User object associated with this todo
        item (many-to-one relationship).
    """
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
