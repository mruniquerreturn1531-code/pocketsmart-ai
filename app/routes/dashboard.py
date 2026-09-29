from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.config import settings

router = APIRouter(tags=["Dashboard & Info"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    user = getattr(request.state, "user", None)
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user, "page_title": "PocketSmart AI - Smart Budget & Recommendation Assistant"})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    user = getattr(request.state, "user", None)
    db = getattr(request.app.state, "db", None)
    recent_history = db.get_user_history(user_id=user["id"], limit=5) if (user and db) else []
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"user": user, "recent_history": recent_history, "page_title": "Dashboard - PocketSmart AI"})

@router.get("/testimonials", response_class=HTMLResponse)
async def testimonials_page(request: Request):
    user = getattr(request.state, "user", None)
    return templates.TemplateResponse(request=request, name="testimonials.html", context={"user": user, "page_title": "Testimonials - PocketSmart AI"})

@router.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.PROJECT_NAME, "version": settings.VERSION, "gemini_model": settings.GEMINI_MODEL, "has_gemini_key": bool(settings.GEMINI_API_KEY)}

@router.get("/startup")
async def startup_check():
    return {"status": "initialized", "service": settings.PROJECT_NAME, "planners": ["Home Interior", "Party Planning", "Jewelry Recommendation"]}
