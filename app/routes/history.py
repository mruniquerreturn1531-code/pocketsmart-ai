from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["History"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    user = getattr(request.state, "user", None)
    if not user: return RedirectResponse(url="/login", status_code=303)
    db = request.app.state.db
    history = db.get_user_history(user_id=user["id"], limit=50)
    return templates.TemplateResponse(request=request, name="history.html", context={"user": user, "history": history, "page_title": "Recommendation History - PocketSmart AI"})

@router.get("/recommendations-details/{rec_id}", response_class=HTMLResponse)
async def recommendation_details_page(rec_id: int, request: Request):
    user = getattr(request.state, "user", None)
    if not user: return RedirectResponse(url="/login", status_code=303)
    db = request.app.state.db
    rec = db.get_recommendation_by_id(rec_id=rec_id, user_id=user["id"])
    if not rec: raise HTTPException(status_code=404, detail="Recommendation record not found")
    return templates.TemplateResponse(request=request, name="recommendations.html", context={"user": user, "result": rec["results"], "recommendation_id": rec["id"], "created_at": rec["created_at"], "page_title": f"Plan #{rec['id']} - PocketSmart AI"})
