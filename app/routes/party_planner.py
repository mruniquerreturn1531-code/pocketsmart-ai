from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.services.gemini_utils import generate_party_recommendations

router = APIRouter(tags=["Party Planner"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/party-planner", response_class=HTMLResponse)
async def party_planner_page(request: Request):
    user = getattr(request.state, "user", None)
    return templates.TemplateResponse(request=request, name="party_planner.html", context={"user": user, "page_title": "Party Budget Planner - PocketSmart AI"})

@router.post("/generate-party")
async def generate_party_endpoint(
    request: Request,
    total_budget: float = Form(...),
    guest_count: int = Form(...),
    event_type: str = Form("Birthday Celebration"),
    venue_type: str = Form("Banquet Hall & Party Lawn")
):
    user = getattr(request.state, "user", None)
    result = generate_party_recommendations(total_budget=total_budget, guest_count=guest_count, event_type=event_type, venue_type=venue_type)
    db = getattr(request.app.state, "db", None)
    recommendation_id = db.save_recommendation(user_id=user["id"], planner_type="Party Planning", total_budget=total_budget, inputs_summary=f"Event: {event_type} | Guests: {guest_count} | Venue: {venue_type}", results=result) if (user and db) else None

    if "application/json" in request.headers.get("accept", ""): return JSONResponse(content=result)
    return templates.TemplateResponse(request=request, name="recommendations.html", context={"user": user, "result": result, "recommendation_id": recommendation_id, "page_title": "Party Budget Recommendations - PocketSmart AI"})
