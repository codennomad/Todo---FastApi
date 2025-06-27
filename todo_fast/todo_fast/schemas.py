from pydantic import BaseModel, ConfigDict, EmailStr

from todo_fast.models import TodoState


class Message(BaseModel):
    """
    Represents a simple message response from the API.

    Attributes:
        message (str): The content of the message.
    """
    message: str


class UserSchemas(BaseModel):
    """
    Schema for user creation and update requests.

    Contains all necessary fields for creating
    a new user or updating
    an existing one, including the plain-text password.

    Attributes:
        username (str): The chosen username for the user.
        email (EmailStr): The email address of the user.
        password (str): The plain-text password for the user.
    """
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """
    Public schema for user data returned by the API.

    This schema exposes user information that is
    safe to share publicly,
    excluding sensitive details like the password.
    It is configured to
    be created from SQLAlchemy ORM models.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
    """
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    """
    Schema for a list of public user profiles.

    Used when returning multiple users, for example,
    from a user listing endpoint.

    Attributes:
        users (list[UserPublic]): A list of `UserPublic` objects.
    """
    users: list[UserPublic]


class Token(BaseModel):
    """
    Schema for access tokens returned upon successful
    authentication or refresh.

    Attributes:
        access_token (str): The JWT string that grants access.
        token_type (str): The type of token, typically "bearer".
    """
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    """
    Base schema for pagination parameters.

    Attributes:
        offset (int): The number of items to skip
        from the beginning. Defaults to 0.
        limit (int): The maximum number of
        items to return. Defaults to 100.
    """
    offset: int = 0
    limit: int = 100


class TodoSchema(BaseModel):
    """
    Schema for creating a new todo item.

    Contains the core information required to define a todo.

    Attributes:
        title (str): The title of the todo item.
        description (str): A more detailed description
        of the todo.
        state (TodoState): The current state of
        the todo item (e.g., 'draft', 'todo').
    """
    title: str
    description: str
    state: TodoState


class TodoPublic(TodoSchema):
    """
    Public schema for todo items returned by the API.

    Extends `TodoSchema` by including the unique
    identifier for the todo.
    This schema is used when returning todo details to clients.

    Attributes:
        id (int): The unique identifier of the todo item.
    """
    id: int


class TodoList(BaseModel):
    """
    Schema for a list of public todo items.

    Used when returning multiple todos, for example,
    from a todo listing endpoint.

    Attributes:
        todos (list[TodoPublic]): A list of `TodoPublic` objects.
    """
    todos: list[TodoPublic]


class FilterTodo(FilterPage):
    """
    Schema for filtering and pagination of todo items.

    Extends `FilterPage` to include optional filtering by title,
    description, and state.

    Attributes:
        title (str | None): Optional. Filter todos by title
        (case-insensitive partial match).
        description (str | None): Optional. Filter todos by
        description (case-insensitive partial match).
        state (TodoState | None): Optional. Filter todos by their
        specific state.
    """
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class TodoUpdate(BaseModel):
    """
    Schema for updating an existing todo item.

    All fields are optional, allowing for partial updates (PATCH requests).

    Attributes:
        title (str | None): Optional. The new title for the todo item.
        description (str | None): Optional. The new description for
        the todo item.
        state (TodoState | None): Optional. The new state for the todo item.
    """
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
