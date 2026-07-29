# 🚆 RailSphere Backend

A production-grade railway reservation backend inspired by the Indian Railways reservation system. Built using modern backend engineering practices with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT Authentication, Redis, Celery, and Docker.

---

## ✨ Features

- 🔐 JWT Authentication
- 👤 User Registration & Login
- 🚉 Railway Station Management
- 🚆 Train Management
- 🗺️ Route & Schedule Management
- 🎟️ Ticket Booking System
- 💺 Automatic Seat Allocation
- ⏳ Waitlist Management
- 💳 Payment Integration
- 📧 Email Notifications
- ⚡ Redis Caching
- 🔄 Background Tasks using Celery
- 🐳 Dockerized Deployment
- 📖 Interactive API Documentation

---

## 🛠 Tech Stack

### Backend

- FastAPI
- SQLAlchemy 2.0 (Async)
- PostgreSQL
- Alembic
- Pydantic v2

### Authentication

- JWT
- Argon2 Password Hashing (pwdlib)

### Infrastructure

- Redis
- Celery
- Docker
- Docker Compose

### Development

- Python 3.13
- Git
- GitHub

---

## 📂 Project Structure

```text
RailSphere/
│
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── dependencies/
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
│
└── README.md
```

---

## 🏗 Architecture

```
                Client
                   │
                   ▼
            FastAPI Routers
                   │
                   ▼
            Service Layer
                   │
                   ▼
          Repository Layer
                   │
                   ▼
     SQLAlchemy Async ORM
                   │
                   ▼
             PostgreSQL
```

---

## 🚀 Getting Started

### Clone

```bash
git clone https://github.com/YOUR_USERNAME/railsphere-backend.git
cd railsphere/backend
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Copy

```text
.env.example
```

to

```text
.env
```

and fill in your values.

### Run Migrations

```bash
alembic upgrade head
```

### Start Server

```bash
uvicorn app.main:app --reload
```

---

## 📖 API Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

## 🛣 Roadmap

- [x] FastAPI Project Setup
- [x] PostgreSQL Integration
- [x] Async SQLAlchemy
- [x] Alembic Migrations
- [x] User Model

### Authentication

- [ ] JWT Authentication
- [ ] User Registration
- [ ] Login
- [ ] Current User

### Railway System

- [ ] Stations
- [ ] Trains
- [ ] Routes
- [ ] Schedules
- [ ] Coaches
- [ ] Seat Allocation
- [ ] Ticket Booking
- [ ] Waitlist
- [ ] Cancellation
- [ ] Fare Calculation

### Infrastructure

- [ ] Redis
- [ ] Celery
- [ ] Docker
- [ ] CI/CD
- [ ] Unit Tests
- [ ] Deployment

---

## 📈 Current Status

Project is actively under development.

Current milestone:

✅ Database foundation completed.

Next milestone:

🔐 JWT Authentication System.

---

## 👨‍💻 Author

**Rohan Tiwari**

- GitHub: https://github.com/rohantiwari9573
- LinkedIn: https://www.linkedin.com/in/rohan-tiwari-012106283/

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub.