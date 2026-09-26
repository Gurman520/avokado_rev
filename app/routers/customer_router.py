from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from app.template_config import templates
from app.auth import get_user_from_cookie
from app.database import SessionLocal
from app.models import Customer, CustomerType
from app.schemas import CustomerCreate

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("/", response_class=HTMLResponse)
async def list_customers(request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    customers = db.query(Customer).all()
    db.close()
    return templates.TemplateResponse(request, "customers.html", {"customers": customers})

@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request, user = Depends(get_user_from_cookie)):
    return templates.TemplateResponse(request, "customer_form.html")

@router.post("/create")
async def create_customer(
    request: Request,
    type: str = Form(...),
    name: str = Form(...),
    phone: str = Form(None),
    legal_address: str = Form(None),
    postal_address: str = Form(None),
    inn: str = Form(None),
    bik: str = Form(None),
    kpp: str = Form(None),
    account_number: str = Form(None),
    corr_account: str = Form(None),
    bank_name: str = Form(None),
    email: str = Form(None),
    user = Depends(get_user_from_cookie)
):
    db = SessionLocal()
    cust = CustomerCreate(
        type=type,
        name=name,
        phone=phone,
        legal_address=legal_address,
        postal_address=postal_address,
        inn=inn,
        bik=bik,
        kpp=kpp,
        account_number=account_number,
        corr_account=corr_account,
        bank_name=bank_name,
        email=email
    )
    db_cust = Customer(**cust.dict())
    db.add(db_cust)
    db.commit()
    db.close()
    return RedirectResponse(url="/customers/?msg=created", status_code=303)

@router.get("/{customer_id}/edit", response_class=HTMLResponse)
async def edit_form(customer_id: int, request: Request, user=Depends(get_user_from_cookie)):
    db = SessionLocal()
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    db.close()
    if not customer:
        raise HTTPException(404, "Заказчик не найден")
    return templates.TemplateResponse(request, "customer_form.html", {"customer": customer})


@router.post("/{customer_id}/edit")
async def edit_customer(
    customer_id: int,
    request: Request,
    type: str = Form(...),
    name: str = Form(...),
    phone: str = Form(None),
    legal_address: str = Form(None),
    postal_address: str = Form(None),
    inn: str = Form(None),
    bik: str = Form(None),
    kpp: str = Form(None),
    account_number: str = Form(None),
    corr_account: str = Form(None),
    bank_name: str = Form(None),
    email: str = Form(None),
    user=Depends(get_user_from_cookie),
):
    db = SessionLocal()
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        db.close()
        raise HTTPException(404, "Заказчик не найден")
    customer.type = CustomerType(type)
    customer.name = name
    customer.phone = phone
    customer.legal_address = legal_address
    customer.postal_address = postal_address
    customer.inn = inn
    customer.bik = bik
    customer.kpp = kpp
    customer.account_number = account_number
    customer.corr_account = corr_account
    customer.bank_name = bank_name
    customer.email = email
    db.commit()
    db.close()
    return RedirectResponse(url="/customers/?msg=saved", status_code=303)
