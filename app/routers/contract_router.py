from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from app.template_config import templates
from app.auth import get_user_from_cookie
from app.database import SessionLocal
from app.models import Contract, Customer, ContractStatus
from datetime import datetime
import os
import uuid

router = APIRouter(prefix="/contracts", tags=["contracts"])
UPLOAD_DIR = "uploads/contracts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def list_contracts(request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    contracts = db.query(Contract).all()
    db.close()
    return templates.TemplateResponse(request, "contracts.html", {"contracts": contracts})

@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    customers = db.query(Customer).all()
    db.close()
    return templates.TemplateResponse(request, "contract_form.html", {"customers": customers})

@router.post("/create")
async def create_contract(
    request: Request,
    number: str = Form(...),
    date: str = Form(...),
    amount: float = Form(...),
    customer_id: int = Form(...),
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
    contract_date = datetime.strptime(date, "%Y-%m-%d").date()
    contract = Contract(
        number=number,
        date=contract_date,
        amount=amount,
        customer_id=customer_id,
        file_path=file_path
    )
    db.add(contract)
    db.commit()
    db.close()
    return RedirectResponse(url="/contracts", status_code=303)

@router.get("/{contract_id}/download")
async def download_contract(contract_id: int, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    db.close()
    if not contract or not contract.file_path:
        from fastapi import HTTPException
        raise HTTPException(404, "Файл договора не найден")
    return FileResponse(contract.file_path, filename=f"contract_{contract.number}.pdf")

@router.get("/{contract_id}/cancel")
async def cancel_contract(contract_id: int, request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if contract:
        contract.status = ContractStatus.CANCELED
        db.commit()
    db.close()
    return RedirectResponse(url="/contracts", status_code=303)