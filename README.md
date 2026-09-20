<<<<<<< HEAD
# rohith
to-do
=======
# 🚀 TaskCraft — Full-Stack Task Management System

**TaskCraft** is a full-stack, production-ready To-Do application built with a modern **Python FastAPI REST API backend**, an embedded **SQLite relational database**, and a responsive **Glassmorphism Single-Page Application (SPA) frontend**.

---

## ✨ Features

- **📊 Interactive Analytics Dashboard**: Real-time counter metrics (Total, Pending, Completed, High Priority) and animated progress bar.
- **🏷️ Task Categories & Priorities**: Organize tasks with categories (*Work, Personal, Shopping, Health, Finance*) and priority tags (*High 🔴, Medium 🟡, Low 🟢*).
- **📅 Due Dates & Overdue Indicators**: Assign target completion dates with relative badges (*Due Today, Due Tomorrow, Overdue*).
- **✅ Subtasks & Checklists**: Create multi-step breakdown checklists for complex tasks with auto-updating progress tracking.
- **🔍 Advanced Search & Filtering**: Real-time debouncing search across titles and descriptions, status tabs, category filters, and sorting choices.
- **🌗 Dark & Light Theme**: Seamless toggle between sleek dark mode and bright light mode with persisted user preference.
- **🛡️ Embedded Database & Zero Config**: Runs out-of-the-box with SQLite (`todos.db`) featuring auto-schema migration and initial seed data.
- **📄 Interactive API Documentation**: Auto-generated Swagger / OpenAPI docs accessible at `/docs`.

---

## 🏗️ Architecture & Stack

| Layer | Technology | Key Details |
| :--- | :--- | :--- |
| **Backend API** | Python `FastAPI` + `uvicorn` | Asynchronous REST endpoints, CORS enabled, Pydantic data validation |
| **Database** | `SQLite3` | Relational tables (`todos`, `subtasks`), foreign key cascades, WAL mode, performance indexes |
| **Frontend UI** | HTML5, Modern Vanilla CSS3, JavaScript | Glassmorphic design system, CSS Custom Properties, fetch API state management |
| **Launcher** | `run.py` | Automated dependency check and single-command local dev server |

---

## 📁 Repository Structure

```
taskcraft-todo/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI server instance & REST API routes
│   ├── database.py          # SQLite connection manager, DAO & schema setup
│   ├── schemas.py           # Pydantic request/response validation models
│   └── data/
│       └── todos.db         # SQLite database file (created automatically)
├── frontend/
│   ├── index.html           # Main SPA HTML structure
│   ├── css/
│   │   └── style.css        # Glassmorphism design system & theme variables
│   └── js/
│       ├── api.js           # REST API fetch wrapper client
│       └── app.js           # State controller, UI renderer & event handlers
├── .gitignore               # Git ignore rules for virtual environments & database
├── pyproject.toml           # Project packaging metadata
├── requirements.txt         # Dependencies list
├── run.py                   # One-click startup launcher script
└── README.md                # Documentation & usage guide
```

---

## ⚡ Quick Start / Local Setup

### Prerequisites
- Python 3.9+ installed on your system.

### 1. Clone the repository
```bash
git clone https://github.com/rohithranp-collab/rohith.git
cd rohith
```

### 2. Run the application
Run the `run.py` launcher script:
```bash
python run.py
```
> The launcher automatically verifies dependencies (`fastapi`, `uvicorn`, `pydantic`), initializes the database schema, seeds sample data, and starts the server!

### 3. Open in Browser
- **Web App UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/todos` | Fetch list of tasks (supports `search`, `status`, `category`, `priority`, `sort_by`) |
| `GET` | `/api/todos/stats` | Retrieve real-time dashboard analytics metrics |
| `POST` | `/api/todos` | Create a new task with optional subtasks |
| `GET` | `/api/todos/{id}` | Get details of a single task by ID |
| `PUT` | `/api/todos/{id}` | Update task details |
| `PATCH` | `/api/todos/{id}/toggle` | Toggle completion status of a task |
| `DELETE` | `/api/todos/{id}` | Delete a task |
| `POST` | `/api/todos/{id}/subtasks` | Add a subtask to an existing task |
| `PATCH` | `/api/subtasks/{sub_id}/toggle` | Toggle completion status of a subtask |
| `DELETE` | `/api/subtasks/{sub_id}` | Delete a subtask |

---

## 📄 License

This project is licensed under the MIT License.
>>>>>>> bc615a8 (Initial commit: Full-stack TaskCraft To-Do Application with FastAPI, SQLite, and Glassmorphism UI)
>>>>>>>
>>>>>>> Web UI Interface: http://127.0.0.1:8000
Interactive OpenAPI Docs: http://127.0.0.1:8000/docs
