from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth import verify_password, create_access_token, get_user_from_cookie
from app.database import SessionLocal
from app.models import User
# from app.template_config import templates


router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
async def login_page(request: Request):
    print("templates:", templates, type(templates))
    return templates.TemplateResponse(request, "login.html")

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})
    token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response
