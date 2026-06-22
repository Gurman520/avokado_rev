from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from app.template_config import templates
from app.auth import get_user_from_cookie
from app.crud import update_user_profile
from app.database import SessionLocal
from app.schemas import UserProfile
from app.models import User

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("", response_class=HTMLResponse)
async def view_profile(request: Request, user = Depends(get_user_from_cookie)):
    return templates.TemplateResponse(request, "profile.html", {"user": user})

@router.post("/edit")
async def edit_profile(
    request: Request,
    full_name: str = Form(...),
    inn: str = Form(...),
    bik: str = Form(None),
    kpp: str = Form(None),
    account_number: str = Form(None),
    bank_name: str = Form(None),
    corr_account: str = Form(None),
    snils: str = Form(None),
    email: str = Form(None),
    passport: str = Form(None),
    user = Depends(get_user_from_cookie)
):
    profile = UserProfile(
        full_name=full_name,
        inn=inn,
        bik=bik,
        kpp=kpp,
        account_number=account_number,
        bank_name=bank_name,
        corr_account=corr_account,
        snils=snils,
        email=email,
        passport=passport
    )
    db = SessionLocal()
    user_db = db.query(User).filter(User.id == user.id).first()
    update_user_profile(db, user_db, profile)
    db.close()
    return RedirectResponse(url="/profile", status_code=303)