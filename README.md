# PMS Modular API - Procurement Supply Module

Production management system with modular architecture. FastAPI backend with async PostgreSQL, Alembic migrations.

---

## Setup Environment

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

### 1. Clone Repository
```bash
git clone <repo-url>
cd AI-PMS--Procurement-Supply_Module
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create `.env` file in project root:
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/procurement_module
```

**Required variables:**
- `DATABASE_URL` - PostgreSQL async connection string. Format: `postgresql+asyncpg://user:password@host:port/dbname`

### 5. Create Database
```bash
createdb procurement_module
```

Or via PostgreSQL:
```sql
CREATE DATABASE procurement_module;
```

### 6. Run Migrations
```bash
alembic upgrade head
```

### 7. Start Server
```bash
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

---

## API Endpoints

### Procurement Orders
- **POST** `/api/v1/procurement/orders` - Create procurement order
- **GET** `/api/v1/procurement/orders` - List all procurement orders

---

## Project Structure

```
app/
├── core/
│   ├── database.py      # Database setup (SQLAlchemy async)
│   └── migrations.py    # Alembic migration runner
├── models/
│   └── models.py        # SQLAlchemy ORM models
├── modules/
│   └── procurement/
│       ├── dtos/        # Data transfer objects (Pydantic schemas)
│       ├── repositories/# Database access layer
│       ├── routers/     # FastAPI routes
│       └── services/    # Business logic
└── main.py              # FastAPI app entry point
```

---

## Development

**Run tests:**
```bash
pytest
```

**Format code:**
```bash
black app/
```

**Lint:**
```bash
flake8 app/
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://postgres:password@localhost/procurement_module` |

---

## Database Migrations

**Create new migration:**
```bash
alembic revision --autogenerate -m "migration description"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```
