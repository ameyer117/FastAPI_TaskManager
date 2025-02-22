# Task Manager

A RESTful Task Manager with JWT authentication, built using FastAPI, PyMongo, Jinja2, and TailwindCSS.

## Overview

This project is a simple task management application that allows users to register, log in, and perform CRUD (Create, Read, Update, Delete) operations on their tasks. It features a secure RESTful API powered by FastAPI, a MongoDB backend via PyMongo, and a server-rendered frontend using Jinja2 templates styled with TailwindCSS. Authentication is handled with JWT (JSON Web Tokens), ensuring that only authenticated users can access their tasks.

## Features

- **User Authentication**: Register and log in with JWT-based authentication.
- **Task Management**: Create, read, update, and delete tasks with a simple web interface.
- **Protected Routes**: API endpoints are secured, accessible only to authenticated users.
- **MongoDB Integration**: Tasks and user data are stored persistently in MongoDB.
- **Responsive Design**: Styled with TailwindCSS for a clean, modern look.
- **Inline JavaScript**: All client-side logic is contained within HTML files, no external JS files.

## Prerequisites

- Python 3.11+
- Docker (for running MongoDB)
- Git

## Setup

1. **Clone the Repository**
   ```bash
   git clone git@github.com:ameyer117/FastAPI_TaskManager.git
   cd task-manager
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start MongoDB with Docker**
   ```bash
   docker-compose up -d
   ```
   This starts a MongoDB instance on `mongodb://localhost:27017/` with a database named `task_manager`.

4. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```
   The app will be available at `http://127.0.0.1:8000`.

## Project Structure

```
task_manager/
├── main.py          # FastAPI application with API and web routes
├── templates/       # Jinja2 HTML templates
│   ├── login.html   # Login page
│   ├── register.html # Registration page
│   └── tasks.html   # Task management page
├── requirements.txt # Python dependencies
└── docker-compose.yml # MongoDB service configuration
```

## Usage

1. **Register**: Visit `http://127.0.0.1:8000/register` to create a new account.
2. **Login**: Go to `http://127.0.0.1:8000/` and log in with your credentials.
3. **Manage Tasks**: After logging in, you’ll be redirected to `/tasks` where you can:
   - Create a new task with a title, description, and status (Pending, In Progress, Completed).
   - View your task list.
   - Edit tasks using a dialog form.
   - Delete tasks with a confirmation prompt.
4. **Logout**: Click the "Logout" button to clear your session and return to the login page.

## API Endpoints

- **POST /api/register**: Register a new user.
- **POST /api/login**: Log in and receive a JWT token.
- **GET /api/tasks**: List all tasks for the authenticated user.
- **POST /api/tasks**: Create a new task.
- **GET /api/tasks/{task_id}**: Retrieve a specific task.
- **PUT /api/tasks/{task_id}**: Update a task.
- **DELETE /api/tasks/{task_id}**: Delete a task.

All task-related endpoints require a valid JWT token in the `Authorization` header (e.g., `Bearer <token>`).

## Development Notes

- **Authentication**: Uses `passlib` for password hashing and `PyJWT` for token generation/validation.
- **Task Status**: Limited to "Pending", "In Progress", and "Completed" via a dropdown.
- **Flicker Mitigation**: Task list updates are handled off-screen to reduce UI flickering.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to contribute by submitting issues or pull requests!
