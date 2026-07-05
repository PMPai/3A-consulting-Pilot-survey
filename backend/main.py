from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import os

from database import Base, engine, BASE_DIR
from routers import surveys, processes, meta, roi, gate

# Create tables on startup (new tables like step_branches auto-created)
Base.metadata.create_all(bind=engine)

# Backward-compatible migration: add new columns to existing process_steps table
with engine.connect() as _conn:
    _cols = [row[1] for row in _conn.exec_driver_sql("PRAGMA table_info(process_steps)")]
    if "is_decision" not in _cols:
        _conn.exec_driver_sql("ALTER TABLE process_steps ADD COLUMN is_decision BOOLEAN DEFAULT 0")
    if "is_merge" not in _cols:
        _conn.exec_driver_sql("ALTER TABLE process_steps ADD COLUMN is_merge BOOLEAN DEFAULT 0")
    if "branch_id" not in _cols:
        _conn.exec_driver_sql(
            "ALTER TABLE process_steps ADD COLUMN branch_id INTEGER "
            "REFERENCES step_branches(id) ON DELETE SET NULL"
        )
    _conn.commit()

app = FastAPI(title="AI 導入需求評估系統", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(surveys.router)
app.include_router(processes.router)
app.include_router(meta.router)
app.include_router(roi.router)
app.include_router(gate.router)

FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")


@app.get("/api")
def api_root():
    return {"name": "AI 導入需求評估 API", "version": "1.0"}


# Serve frontend static files
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")


@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/client/survey", response_class=HTMLResponse)
def client_survey():
    return FileResponse(os.path.join(FRONTEND_DIR, "client", "survey.html"))


@app.get("/consultant/dashboard", response_class=HTMLResponse)
def consultant_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "consultant", "dashboard.html"))


@app.get("/consultant/detail", response_class=HTMLResponse)
def consultant_detail():
    return FileResponse(os.path.join(FRONTEND_DIR, "consultant", "detail.html"))
