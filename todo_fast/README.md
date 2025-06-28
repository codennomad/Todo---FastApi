# Todo-FastAPI

[![CI](https://github.com/codennomad/Todo-FastApi/actions/workflows/pipeline.yaml/badge.svg)](https://github.com/codennomad/Todo-FastApi/actions)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Version](https://img.shields.io/badge/version-0.5.1-informational.svg)
![Poetry](https://img.shields.io/badge/Poetry-managed-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-success.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

> A modern, production-ready RESTful API for managing tasks — built with FastAPI, tested with Pytest, automated with GitHub Actions, and packaged with Poetry.

---

## ✨ Overview

**Todo-FastAPI** is a scalable backend designed for high code quality, fast iteration, and clean architecture. It includes:

- ⚡️ FastAPI backend with automatic OpenAPI documentation
- 🧪 Full test coverage using Pytest
- 🔁 CI pipeline using GitHub Actions (Python 3.11, Poetry, Secrets)
- 📚 Complete docstring coverage across the codebase
- 🧩 Modular design for easy extension and production deployment

---

## ✅ Features

- Full CRUD for tasks: Create, Read, Update, Delete
- Task fields include: title, description, and status (`pending`, `in-progress`, `done`)
- Auth logic ready to integrate (token-based system using JWT)
- CI runs automated tests on every push and pull request

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11
- [Poetry](https://python-poetry.org/)
- Git

### Installation

```bash
git clone https://github.com/codennomad/Todo-FastApi.git
cd Todo-FastApi
poetry install
poetry shell
```

## Environment Variables
Create a .env file in the root with:
```bash
DATABASE_URL=sqlite:///./db.sqlite3
SECRET_KEY=your_super_secret_key
```

## Running the Application

```bash
uvicorn todo_fast.app:app --reload
```
>Then visit: http://localhost:8000/docs

## 🧪 Running Tests

```bash
poetry run task test
```
> Tests are executed automatically on every push via GitHub Actions.

---

## 🧠 Project Structure

```bash
todo_fast/
├── main.py             # FastAPI entry point
├── models.py           # Data models (SQLModel)
├── schemas.py          # Pydantic validation schemas
├── crud.py             # Core business logic
├── security.py         # Auth & token management
├── tests/              # Automated tests
└── .github/workflows/  # CI pipeline definition
```

## 📦 Versioning

Current version: v0.5.1

```bash
git tag -a v0.5.1 -m "v0.5.1: Add CI pipeline, full docstrings and tests"
git push origin v0.5.1
```

## 🔧 Roadmap

 Add JWT-based authentication

 PostgreSQL support

 Dockerized deployment with docker-compose

 Optional frontend with React or Svelte

 Add OpenAPI-compatible API versioning

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

1. Fork the repo

2. **Create your feature branch**: git checkout -b feature/my-feature

3. **Commit your changes**: git commit -m 'feat: add new feature'

4. **Push to the branch**: git push origin feature/my-feature

5. Open a pull request

---

## 📝 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## ⚡ Final Note

>This repository represents a personal commitment to code quality, automation, and developer-first architecture. Built with care, tested with precision, and ready for real-world use.

---

## 🙋‍♂️ Author

Gabriel Henrique 

🔗 [LinkedIn](https://www.linkedin.com/in/gabrielhenrique-tech/)

📧 gabrielheh03@gmail.com