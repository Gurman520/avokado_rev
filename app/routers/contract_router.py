from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from app.template_config import templates
from app.auth import get_user_from_cookie
from app.database import SessionLocal
from app.models import Contract, Customer, ContractStatus
from datetime import datetime
from app.pdf_service import html_to_pdf
import os
import uuid
from sqlalchemy.orm import joinedload


router = APIRouter(prefix="/contracts", tags=["contracts"])
UPLOAD_DIR = "uploads/contracts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

PDF_DIR = "generated_contracts"
os.makedirs(PDF_DIR, exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def list_contracts(request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    contracts = db.query(Contract).options(joinedload(Contract.customer)).all()
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
    return RedirectResponse(url="/contracts/?msg=cancelled", status_code=303)

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
    return RedirectResponse(url="/contracts/?msg=cancelled", status_code=303)

@router.get("/{contract_id}/edit", response_class=HTMLResponse)
async def edit_form(contract_id: int, request: Request, user=Depends(get_user_from_cookie)):
    db = SessionLocal()
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    customers = db.query(Customer).all()
    db.close()
    if not contract:
        raise HTTPException(404, "Договор не найден")
    return templates.TemplateResponse(request, "contract_form.html", {
        "contract": contract,
        "customers": customers,
    })


@router.post("/{contract_id}/edit")
async def edit_contract(
    contract_id: int,
    request: Request,
    number: str = Form(...),
    date: str = Form(...),
    amount: float = Form(None),
    customer_id: int = Form(...),
    status: str = Form(None),
    file: UploadFile = File(None),
    user=Depends(get_user_from_cookie),
):
    db = SessionLocal()
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        db.close()
        raise HTTPException(404, "Договор не найден")

    contract.number = number
    contract.date = datetime.strptime(date, "%Y-%m-%d").date()
    contract.amount = amount
    contract.customer_id = customer_id
    if status:
        contract.status = ContractStatus(status)

    if file and file.filename:
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        contract.file_path = file_path

    db.commit()
    db.close()
    return RedirectResponse(url="/contracts/?msg=saved", status_code=303)

@router.get("/{contract_id}/generate")
async def generate_contract_pdf(
    contract_id: int,
    user=Depends(get_user_from_cookie),
):
    db = SessionLocal()
    contract = (
        db.query(Contract)
        .options(joinedload(Contract.customer))
        .filter(Contract.id == contract_id)
        .first()
    )
    if not contract:
        db.close()
        raise HTTPException(404, "Договор не найден")

    template = templates.get_template("contract_pdf_template.html")
    html_content = template.render(
        contract=contract,
        customer=contract.customer,
        user=user,
    )
    filename = f"contract_{contract.id}_{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(PDF_DIR, filename)
    html_to_pdf(html_content, pdf_path)
    db.close()
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"contract_{contract.number}.pdf")
