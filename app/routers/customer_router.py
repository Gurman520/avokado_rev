from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from app.template_config import templates
from app.auth import get_user_from_cookie
from app.database import SessionLocal
from app.models import Customer
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
    return RedirectResponse(url="/customers", status_code=303)