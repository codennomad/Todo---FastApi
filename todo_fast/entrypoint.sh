#!/bin/sh

#exec migration
poetry run alembic upgrade head

#Init 
poetry run uvicorn --host 0.0.0.0 --port 8000 todo_fast.app:app