# SAP FastAPI – Medication Monitoring API

A FastAPI backend for a medication monitoring system.  
This project provides secure CRUD endpoints for **users, devices, schedules, and medication logs**, designed to integrate with Android apps and IoT devices (ESP32).

---

## 🚀 Features
- **User Authentication** with JWT (login/register).
- **Schedules Management**: create, list, mark as taken/snooze.
- **Medication Logs**: track adherence history.
- **Device Integration**: assign schedules to devices.
- **Dockerized Deployment**: reproducible environment with PostgreSQL.
- **Swagger UI** available at `/docs`.

---

## 📦 Tech Stack
- [FastAPI](https://fastapi.tiangolo.com/) – web framework
- [Uvicorn](https://www.uvicorn.org/) – ASGI server
- [SQLAlchemy](https://www.sqlalchemy.org/) – ORM
- [Databases](https://www.encode.io/databases/) – async DB layer
- [PostgreSQL](https://www.postgresql.org/) – database
- [Docker](https://www.docker.com/) – containerization
- [JWT](https://jwt.io/) – authentication

---

## 🛠 Setup

### 1. Clone Repository
```bash
git clone git@github.com:fuuyuki/sap-fastapi.git
cd sap-fastapi
```
### 2. Environment Variables
Create a .env file:
```env
DATABASE_URL=postgresql+psycopg2://sapuser:yourpassword@db/sapfastapi
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
### 3. Requirements (if running locally)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

###4. Run with Docker
```bash
docker-compose up -d --build
```
Access API at:
```code
http://localhost:8000/docs
```

### 📂 Project Structure
```code
sap-fastapi/
│── app/
│   ├── main.py          # FastAPI entrypoint
│   ├── database.py      # DB connection
│   ├── crud.py          # CRUD operations
│   ├── schemas.py       # Pydantic models
│   └── auth.py          # JWT authentication
│── requirements.txt
│── Dockerfile
│── docker-compose.yml
│── README.md
```

### 🔄 Deployment on VPS
1. Install Docker + Docker Compose.
2. Clone repo:
```bash
git clone git@github.com:fuuyuki/sap-fastapi.git
cd sap-fastapi
```
3. Run:
```bash
docker-compose up -d --build
```
4. Configure Nginx reverse proxy + HTTPS (Certbot).

### 📌 API Endpoints (Summary)
- Auth
> POST /register
> POST /login

- Devices
> GET /devices/
> POST /devices/

- Schedules
> GET /schedules/
> POST /schedules/

- Medlogs
> GET /medlogs/
> POST /medlogs/
>

### ✅ Next Steps
- Integrate with Android app (Dashboard, Schedule, Logs, Add Medication).
- Connect ESP32 devices for real‑time medication tracking.
- Add Alembic migrations for schema evolution.

### 📄 License
MIT License – feel free to use and adapt.
