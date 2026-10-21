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

### 4. Run with Docker
```bash
docker-compose up -d --build
```
Access API at:
```code
http://localhost:8080/docs
```

#### Database (created automatically)
You do **not** need a PostgreSQL server on the host machine. The `db`
service creates the `sapdb` database and loads the schema + seed data from
`db/init.sql` on first start. The API container waits until PostgreSQL is
healthy before starting.

The init script only runs when the data volume is empty. To wipe the
database and re-seed it from `db/init.sql`:
```bash
docker-compose down -v
docker-compose up -d --build
```

If a local PostgreSQL already occupies port `5432`, publish the container on
a different port (this does not affect the API, which connects over the
Docker network):
```bash
DB_PORT=5433 docker-compose up -d --build
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

### 📷 Medication evidence (Android camera)

The ESP32 remains the source of truth for `taken` / `missed`. The Android app
can attach an optional camera snapshot + confidence to an existing medlog as
additional proof.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `PUT` | `/medlogs/{medlog_id}/evidence` | Patient JWT | Multipart: `photo`, `confidence` (0..1), optional `captured_at`, `method` |
| `GET` | `/medlogs/{medlog_id}/evidence` | Patient or caretaker JWT | Returns the stored JPEG |
| `DELETE` | `/medlogs/{medlog_id}/evidence` | Patient JWT | Removes the snapshot |

Snapshots are re-encoded server-side (max 480px JPEG, EXIF/GPS stripped) and
stored under `MEDIA_DIR` (default `media/`, `/app/media` inside Docker).
Uploads are capped at 5 MB; the stored file is usually only tens of KB.

For an existing database volume, apply the column migration once:
```bash
docker compose exec -T db psql -U fauxpg -d sapdb < db/migrations/002_medlog_evidence.sql
```

### ✅ Next Steps
- Integrate with Android app (Dashboard, Schedule, Logs, Add Medication).
- Connect ESP32 devices for real‑time medication tracking.
- Add Alembic migrations for schema evolution.

### 📄 License
MIT License – feel free to use and adapt.
