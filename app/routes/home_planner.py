import json
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, List
from app.services.gemini_utils import generate_home_recommendations

router = APIRouter(tags=["Home Planner"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/home-planner", response_class=HTMLResponse)
async def home_planner_page(request: Request):
    user = getattr(request.state, "user", None)
    return templates.TemplateResponse(request=request, name="home_planner.html", context={"user": user, "page_title": "Home Interior Budget Planner - PocketSmart AI"})

@router.post("/generate-home")
async def generate_home_endpoint(
    request: Request,
    total_budget: float = Form(...),
    rooms: List[str] = Form([]),
    style: str = Form("Modern & Functional"),
    items_json: Optional[str] = Form(None)
):
    user = getattr(request.state, "user", None)
    items_requested = []
    if items_json:
        try: items_requested = json.loads(items_json)
        except Exception: pass
            
    if not items_requested:
        if not rooms: rooms = ["Living Room", "Bedroom"]
        for room in rooms:
            if room == "Living Room":
                items_requested.extend([{"room": "Living Room", "item": "Sofa Set & Cushions", "qty": 1}, {"room": "Living Room", "item": "Warm LED Ceiling Fan", "qty": 1}])
            elif room == "Bedroom":
                items_requested.extend([{"room": "Bedroom", "item": "Queen Storage Bedframe", "qty": 1}, {"room": "Bedroom", "item": "Bedside Reading Lamp", "qty": 2}])
            else:
                items_requested.append({"room": room, "item": f"{room} Accent Decor", "qty": 1})
                
    result = generate_home_recommendations(total_budget=total_budget, rooms=rooms, items_requested=items_requested, style=style)
    db = getattr(request.app.state, "db", None)
    recommendation_id = db.save_recommendation(user_id=user["id"], planner_type="Home Interior", total_budget=total_budget, inputs_summary=f"Rooms: {', '.join(rooms)} | Style: {style}", results=result) if (user and db) else None

    if "application/json" in request.headers.get("accept", ""): return JSONResponse(content=result)
    return templates.TemplateResponse(request=request, name="recommendations.html", context={"user": user, "result": result, "recommendation_id": recommendation_id, "page_title": "Home Interior Recommendations - PocketSmart AI"})
