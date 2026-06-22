from sqlalchemy.orm import Session
from app.models import User, Customer, Contract, Cheque, Act, ServiceItem
from app.schemas import UserProfile, CustomerCreate, ContractCreate, ChequeCreate, ActCreate
from datetime import date
import os

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def update_user_profile(db: Session, user: User, profile: UserProfile):
    user.full_name = profile.full_name
    user.inn = profile.inn
    user.bik = profile.bik
    user.kpp = profile.kpp
    user.account_number = profile.account_number
    user.bank_name = profile.bank_name
    user.corr_account = profile.corr_account
    user.snils = profile.snils
    user.email = profile.email
    user.passport = profile.passport
    db.commit()
    db.refresh(user)
    return user

def get_customers(db: Session):
    return db.query(Customer).all()

def create_customer(db: Session, c: CustomerCreate):
    db_cust = Customer(**c.dict())
    db.add(db_cust)
    db.commit()
    db.refresh(db_cust)
    return db_cust

def get_contracts(db: Session):
    return db.query(Contract).all()

def create_contract(db: Session, c: ContractCreate, file_path: str = None):
    db_contract = Contract(**c.dict(), file_path=file_path)
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

def get_cheques(db: Session, contract_id: int = None):
    q = db.query(Cheque)
    if contract_id:
        q = q.filter(Cheque.contract_id == contract_id)
    return q.all()

def create_cheque(db: Session, ch: ChequeCreate, file_path: str = None):
    db_cheque = Cheque(**ch.dict(), file_path=file_path)
    db.add(db_cheque)
    db.commit()
    db.refresh(db_cheque)
    return db_cheque

def get_acts(db: Session):
    return db.query(Act).all()

def create_act(db: Session, act_data: ActCreate, file_path: str = None):
    if not act_data.number:
        last_act = db.query(Act).order_by(Act.id.desc()).first()
        act_data.number = f"АКТ-{(last_act.id + 1) if last_act else 1:04d}"
    db_act = Act(
        number=act_data.number,
        date=act_data.date,
        contract_id=act_data.contract_id,
        customer_id=act_data.customer_id,
        pdf_path=file_path
    )
    db.add(db_act)
    db.flush()
    if act_data.services:
        for s in act_data.services:
            db.add(ServiceItem(description=s.description, quantity=s.quantity, unit_price=s.unit_price, act_id=db_act.id))
    db.commit()
    db.refresh(db_act)
    return db_act