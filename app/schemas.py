from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserProfile(BaseModel):
    full_name: str
    inn: str
    bik: Optional[str] = None
    kpp: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    corr_account: Optional[str] = None
    snils: Optional[str] = None
    email: Optional[str] = None
    passport: Optional[str] = None

class CustomerCreate(BaseModel):
    type: str = "legal"  # legal или individual
    name: str
    phone: Optional[str] = None
    legal_address: Optional[str] = None
    postal_address: Optional[str] = None
    inn: Optional[str] = None
    bik: Optional[str] = None
    kpp: Optional[str] = None
    account_number: Optional[str] = None
    corr_account: Optional[str] = None
    bank_name: Optional[str] = None
    email: Optional[str] = None

class ContractCreate(BaseModel):
    number: str
    date: date
    amount: float
    customer_id: int
    # file будет обрабатываться отдельно через UploadFile

class ChequeCreate(BaseModel):
    link: str
    date: date
    amount: float
    contract_id: int
    act_id: Optional[int] = None   # новая связь

class ServiceItemSchema(BaseModel):
    description: str
    quantity: float = 1
    unit_price: float = 0

class ActCreate(BaseModel):
    number: Optional[str] = None
    date: date
    contract_id: Optional[int] = None   # теперь необязательно
    customer_id: Optional[int] = None   # для прямого указания заказчика (если нет договора)
    generate_pdf: bool = False
    services: Optional[List[ServiceItemSchema]] = None