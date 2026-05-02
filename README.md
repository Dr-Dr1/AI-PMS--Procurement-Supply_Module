# AI-PMS: Procurement & Supply Chain Module

A premium, high-performance modular system for managing procurement lifecycles, supply chain logistics, and material scheduling. Built with a modern FastAPI backend and a responsive Vanilla JS frontend featuring glassmorphism aesthetics.

---

## 🛠️ Getting Started (Recommended)

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 15+

### 2. Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the template to create your environment file:
```bash
cp .env.example .env
```
> [!IMPORTANT]
> A `.env` file is intentionally used for local development to manage sensitive database credentials and configuration. Ensure it is updated with your local PostgreSQL details.

### 4. Database Initialization
```bash
alembic upgrade head
```

### 5. Run Development Server
```bash
uvicorn app.main:app --reload
```

---

## 🐳 Docker Setup (Alternative / Troubleshooting)

If you encounter any issues with local dependencies or database configuration, use Docker as a **second option** to run the project in a guaranteed environment.

1. **Launch**:
   ```bash
   docker-compose up -d --build
   ```
2. **Access**:
   - **Frontend/API**: `http://localhost:8000`
   - **API Docs**: `http://localhost:8000/docs`


---

## 🧠 Knowledge Graph (Graphify)

This project uses **Graphify** to maintain a persistent knowledge graph of the codebase architecture, relationships, and design rationale.

- **Interactive Graph**: Open `graphify-out/graph.html` in your browser to explore the system architecture visually.
- **Architectural Report**: See `graphify-out/GRAPH_REPORT.md` for a summary of core components and "God Nodes".
- **Query the Graph**: If using an AI assistant with the Graphify skill, you can ask deep architectural questions like:
  ```
  /graphify query "How does the Indent approval flow connect to Purchase Orders?"
  ```

---

## 📂 Project Structure

```bash
├── app/                  # FastAPI Backend
│   ├── core/             # Database config, Migrations, Enums
│   ├── models/           # SQLAlchemy ORM Models
│   └── modules/          # Domain-driven Modules (Procurement, etc.)
│       └── procurement/  # Services, Repositories, Routers, DTOs
├── frontend/             # Vanilla JS Frontend (SPA)
│   ├── css/              # Design System & Styling
│   ├── js/               # ES Modules (App, API, Views)
│   └── index.html        # Main Entry Point
├── docs/                 # API & Phase Documentation
├── alembic/              # Database Migrations
└── graphify-out/         # AI-generated Knowledge Graph
```

---

## ✨ Features
- **Modular ES6 Frontend**: No build tools required, pure high-performance JavaScript.
- **Glassmorphism UI**: Premium design system with backdrop blurs and entrance animations.
- **Automated Lifecycle**: Handles Indents → POs → FAT → Deliveries.
- **Containerized**: Fully portable via Docker Compose.
- **Knowledge-Aware**: Integrated Graphify support for better developer onboarding.

---

## 🤝 Development Guidelines
- **ES Modules**: Always use `import/export` for frontend scripts.
- **Migrations**: Use `alembic revision --autogenerate` for schema changes.
- **Styling**: Stick to the CSS variables defined in `styles.css` to maintain theme consistency.

---

## 📄 License
Internal AI-PMS Project.
