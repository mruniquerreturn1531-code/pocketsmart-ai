from fastapi import APIRouter, Request, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.config import settings
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(tags=["Authentication"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = getattr(request.state, "user", None)
    if user: return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="register.html", context={"user": user, "page_title": "Register - PocketSmart AI"})

@router.post("/register")
async def register_submit(request: Request, response: Response, username: str = Form(...), email: str = Form(...), password: str = Form(...), full_name: str = Form(None)):
    db = request.app.state.db
    if db.get_user_by_username(username): return templates.TemplateResponse(request=request, name="register.html", context={"error": "Username taken.", "page_title": "Register - PocketSmart AI"})
    if db.get_user_by_email(email): return templates.TemplateResponse(request=request, name="register.html", context={"error": "Email registered.", "page_title": "Register - PocketSmart AI"})

    new_user = db.create_user(username=username, email=email, password_hash=hash_password(password), full_name=full_name)
    token = create_access_token(data={"sub": new_user["username"], "user_id": new_user["id"]})
    redirect_resp = RedirectResponse(url="/dashboard", status_code=303)
    redirect_resp.set_cookie(key=settings.COOKIE_NAME, value=token, httponly=True, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, samesite="lax")
    return redirect_resp

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = getattr(request.state, "user", None)
    if user: return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"user": user, "page_title": "Login - PocketSmart AI"})

@router.post("/login")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    db = request.app.state.db
    user = db.get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Invalid credentials.", "page_title": "Login - PocketSmart AI"})

    token = create_access_token(data={"sub": user["username"], "user_id": user["id"]})
    redirect_resp = RedirectResponse(url="/dashboard", status_code=303)
    redirect_resp.set_cookie(key=settings.COOKIE_NAME, value=token, httponly=True, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, samesite="lax")
    return redirect_resp

@router.get("/logout")
async def logout():
    redirect_resp = RedirectResponse(url="/", status_code=303)
    redirect_resp.delete_cookie(key=settings.COOKIE_NAME)
    return redirect_resp
