from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from app.template_config import templates
from app.auth import get_user_from_cookie
from app.database import SessionLocal
from app.models import Act, ActStatus, Contract, ServiceItem, User, Customer, ContractStatus
from app.schemas import ActCreate, ServiceItemSchema
from app.pdf_service import html_to_pdf      # <-- НАШ МОДУЛЬ
from datetime import datetime
import os
import json
import uuid
from sqlalchemy.orm import joinedload



router = APIRouter(prefix="/acts", tags=["acts"])
UPLOAD_DIR = "uploads/acts"
PDF_DIR = "generated_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def list_acts(request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    acts = db.query(Act).options(
        joinedload(Act.contract).joinedload(Contract.customer),
        joinedload(Act.customer)
    ).all()
    db.close()
    return templates.TemplateResponse(request, "acts.html", {"acts": acts})

@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request, user=Depends(get_user_from_cookie)):
    db = SessionLocal()
    contracts = (
        db.query(Contract)
        .options(joinedload(Contract.customer))          # <-- подгружаем заказчика
        .filter(Contract.status == ContractStatus.ACTIVE)
        .all()
    )
    customers = db.query(Customer).all()
    db.close()
    return templates.TemplateResponse(request, "act_form.html", {
        "contracts": contracts,
        "customers": customers,
    })

@router.post("/create")
async def create_act(
    request: Request,
    date: str = Form(...),
    contract_id: int = Form(None),      # теперь необязательно
    customer_id: int = Form(None),      # если договор не выбран
    total_amount: float = Form(None),
    generate_pdf: bool = Form(False),
    services_json: str = Form("[]"),
    file: UploadFile = File(None),
    user: User = Depends(get_user_from_cookie)
):
    db = SessionLocal()
    # генерация номера
    last_act = db.query(Act).order_by(Act.id.desc()).first()
    number = f"АКТ-{(last_act.id + 1) if last_act else 1:04d}"
    act_date = datetime.strptime(date, "%Y-%m-%d").date()

    # Если не указан договор, должен быть указан customer_id
    if not contract_id and not customer_id:
        db.close()
        raise HTTPException(400, "Необходимо выбрать договор или заказчика")

    if generate_pdf:
        services_list = json.loads(services_json)
        act = Act(
            number=number,
            date=act_date,
            status=ActStatus.PDF_GENERATED,
            contract_id=contract_id if contract_id else None,
            customer_id=customer_id if customer_id else None,
            total_amount=total_amount if total_amount is not None else computed_total
        )
        db.add(act)
        db.flush()
        for s in services_list:
            db.add(ServiceItem(
                description=s["description"],
                quantity=float(s["quantity"]),
                unit_price=float(s["unit_price"]),
                act_id=act.id
            ))
        db.commit()

        # Генерация PDF
        if contract_id:
            contract = db.query(Contract).filter(Contract.id == contract_id).first()
            customer = contract.customer
        else:
            contract = None
            customer = db.query(Customer).filter(Customer.id == customer_id).first()

        template = templates.get_template("act_pdf_template.html")
        html_content = template.render(
            act=act, user=user, customer=customer, contract=contract, services=act.services
        )
        filename = f"act_{act.id}_{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(PDF_DIR, filename)
        html_to_pdf(html_content, pdf_path)
        act.pdf_path = pdf_path
        db.commit()
    else:
        # Пустой акт (можно прикрепить файл)
        file_path = None
        if file and file.filename:
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        act = Act(
            number=number,
            date=act_date,
            status=ActStatus.EMPTY if not file_path else ActStatus.PDF_GENERATED,
            contract_id=contract_id if contract_id else None,
            customer_id=customer_id if customer_id else None,
            pdf_path=file_path,
            total_amount=total_amount
        )
        db.add(act)
        db.commit()
    db.close()
    return RedirectResponse(url="/acts/?msg=created", status_code=303)

@router.get("/{act_id}/download")
async def download_act(act_id: int, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    act = db.query(Act).filter(Act.id == act_id).first()
    db.close()
    if not act or not act.pdf_path:
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(act.pdf_path, media_type="application/pdf", filename=f"act_{act.number}.pdf")

@router.get("/{act_id}/edit", response_class=HTMLResponse)
async def edit_form(act_id: int, request: Request, user=Depends(get_user_from_cookie)):
    db = SessionLocal()
    act = (
        db.query(Act)
        .options(joinedload(Act.services))
        .filter(Act.id == act_id)
        .first()
    )
    if not act:
        db.close()
        raise HTTPException(404, "Акт не найден")
    if act.status == ActStatus.CANCELED:
        db.close()
        raise HTTPException(400, "Акт аннулирован, редактирование невозможно")
    
    contracts = (
        db.query(Contract)
        .options(joinedload(Contract.customer))
        .all()
    )
    customers = db.query(Customer).all()
    db.close()
    if not act:
        raise HTTPException(404, "Акт не найден")
    return templates.TemplateResponse(request, "act_edit_form.html", {
        "act": act,
        "contracts": contracts,
        "customers": customers,
    })


@router.post("/{act_id}/edit")
async def edit_act(
    act_id: int,
    request: Request,
    date: str = Form(...),
    total_amount: float = Form(None),
    contract_id: int = Form(None),
    customer_id: int = Form(None),
    file: UploadFile = File(None),
    user=Depends(get_user_from_cookie),
):
    db = SessionLocal()
    act = db.query(Act).filter(Act.id == act_id).first()
    if not act:
        db.close()
        raise HTTPException(404, "Акт не найден")
    act.date = datetime.strptime(date, "%Y-%m-%d").date()
    act.total_amount = total_amount
    act.contract_id = contract_id or None
    act.customer_id = customer_id or None

    if file and file.filename:
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        act.pdf_path = file_path
        act.status = ActStatus.PDF_GENERATED

    db.commit()
    db.close()
    return RedirectResponse(url="/acts/?msg=saved", status_code=303)

@router.get("/{act_id}/cancel")
async def cancel_act(act_id: int, user=Depends(get_user_from_cookie)):
    db = SessionLocal()
    act = db.query(Act).filter(Act.id == act_id).first()
    if not act:
        db.close()
        raise HTTPException(404, "Акт не найден")
    act.status = ActStatus.CANCELED
    db.commit()
    db.close()
    return RedirectResponse(url="/acts/?msg=cancelled", status_code=303)
