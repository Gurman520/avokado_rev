from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from app.template_config import templates
from app.auth import get_user_from_cookie
from app.database import SessionLocal
from app.models import Cheque, Contract, Act
from datetime import datetime
import os
import uuid

router = APIRouter(prefix="/cheques", tags=["cheques"])
UPLOAD_DIR = "uploads/cheques"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def list_cheques(request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    cheques = db.query(Cheque).all()
    db.close()
    return templates.TemplateResponse(request, "cheques.html", {"cheques": cheques})

@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    contracts = db.query(Contract).filter(Contract.status == "Активен").all()
    # Получаем все акты для выбора
    acts = db.query(Act).all()
    db.close()
    return templates.TemplateResponse(request, "cheque_form.html", {
        "contracts": contracts,
        "acts": acts
    })

@router.post("/create")
async def create_cheque(
    request: Request,
    link: str = Form(...),
    date: str = Form(...),
    amount: float = Form(...),
    contract_id: int = Form(...),
    act_id: int = Form(None),
    file: UploadFile = File(None),
    user = Depends(get_user_from_cookie)
):
    file_path = None
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    db = SessionLocal()
    cheque_date = datetime.strptime(date, "%Y-%m-%d").date()
    cheque = Cheque(
        link=link,
        date=cheque_date,
        amount=amount,
        contract_id=contract_id,
        act_id=act_id if act_id else None,
        file_path=file_path
    )
    db.add(cheque)
    db.commit()
    db.close()
    return RedirectResponse(url="/cheques", status_code=303)