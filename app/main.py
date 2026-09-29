import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db_instance
from app.routes import dashboard, home_planner, party_planner, jewelry_planner, auth, history

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, description=settings.DESCRIPTION)
app.state.db = db_instance

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
os.makedirs(static_dir / "uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.middleware("http")
async def extract_user_session_middleware(request: Request, call_next):
    token = request.cookies.get(settings.COOKIE_NAME)
    request.state.user = None
    if token:
        try:
            from app.security import decode_access_token
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                user = db_instance.get_user_by_username(payload["sub"])
                if user: request.state.user = user
        except Exception: pass
    return await call_next(request)

app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(home_planner.router)
app.include_router(party_planner.router)
app.include_router(jewelry_planner.router)
app.include_router(history.router)
