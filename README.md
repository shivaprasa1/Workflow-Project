# Smart Workflow Management System

A role-based workflow and task management system built with Python, FastAPI, MySQL, and SQLAlchemy.

The system allows administrators, managers, and employees to manage users, assign tasks, track progress, and receive notifications.

## 1. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | MySQL 8.0 |
| ORM | SQLAlchemy |
| Database migrations | Alembic |
| Authentication | JWT |
| Password hashing | Argon2 |
| Testing | Pytest |
| API documentation | Swagger UI |

## 2. User Roles

- **Admin:** Manage users, roles, account status, and system tasks.
- **Manager:** Create and assign tasks and monitor their team's work.
- **Employee:** View assigned tasks, update progress, and submit completed work.

## 3. Project Structure

```text
smart-workflow-management-system/
│
├── app/
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── utils/
│
├── migrations/
│   └── versions/
│
├── scripts/
├── tests/
│
├── .env
├── .gitignore
├── alembic.ini
├── main.py
├── requirements.txt
└── README.md
```

## 4. Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
cd smart-workflow-management-system
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## 5. Database Configuration

Install and start MySQL 8.0.

Create a database named:

```sql
CREATE DATABASE workflow_db;
```

Create a `.env` file in the project root:

```env
DB_HOST=127.0.0.1
DB_PORT=3307
DB_NAME=workflow_db
DB_USER=workflow_app
DB_PASSWORD=your_database_password

JWT_SECRET_KEY=your_secure_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace the example credentials with your own values.

**Important:** Never commit `.env` or expose database credentials and JWT secrets.

## 6. Database Migrations

This project uses Alembic to manage database schema changes.

Check the current migration:

```powershell
python -m alembic current
```

View available migration heads:

```powershell
python -m alembic heads
```

Generate a migration after changing SQLAlchemy models:

```powershell
python -m alembic revision --autogenerate -m "describe your changes"
```

Review the generated migration before applying it.

Apply migrations:

```powershell
python -m alembic upgrade head
```

## 7. Run the Application

Start the FastAPI development server:

```powershell
python -m uvicorn main:app --reload
```

The application runs at:

http://127.0.0.1:8000

### API Documentation

Swagger UI:

http://127.0.0.1:8000/docs

ReDoc:

http://127.0.0.1:8000/redoc

Health check:

http://127.0.0.1:8000/health

## 8. Implemented API Modules

| Module | Functionality |
|---|---|
| Registration | Employee registration |
| Authentication | Login, JWT authentication, current user |
| User Management | List users, update roles and account status |
| Task Management | Create, assign, retrieve, and update tasks |
| Dashboard | Task statistics and employee workload |
| Notifications | Notification history, unread count, mark as read |

## 9. Run Automated Tests

Execute the complete test suite:

```powershell
python -m pytest -v
```

The tests use an isolated in-memory SQLite database, keeping the development MySQL database separate.

Latest verified result:

**30 tests passed.**

## 10. Security Features

- Password hashing using Argon2.
- JWT-based authentication.
- Role-based access control.
- Protected API endpoints.
- Active account verification.
- Input validation using Pydantic.
- User-specific task and notification access restrictions.
- Environment-based secret configuration.

## 11. Planned Enhancements

- AI-powered task classification and priority recommendations using OpenRouter.
- AI-generated task summaries.
- Push notifications using Firebase Cloud Messaging.
- React.js web application.
- React Native Android application.
- Docker-based deployment.
- Cloud hosting and production configuration.

## 12. Project Objective

The objective is to build a centralized workflow management platform that improves task assignment, employee productivity, progress tracking, and communication through a shared backend and database.

**Project Status:** Backend core implementation completed; further security review, AI integration, frontend development, and deployment are planned.