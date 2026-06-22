from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ContractStatus(str, enum.Enum):
    ACTIVE = "Активен"
    CANCELED = "Аннулирован"

class ActStatus(str, enum.Enum):
    EMPTY = "Пустой"
    PDF_GENERATED = "PDF сгенерирован"

class CustomerType(str, enum.Enum):
    LEGAL = "legal"
    INDIVIDUAL = "individual"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    inn = Column(String, nullable=False)
    bik = Column(String)
    kpp = Column(String)
    account_number = Column(String)
    bank_name = Column(String)
    # Новые поля
    corr_account = Column(String)          # корр. счёт банка
    snils = Column(String)                 # СНИЛС
    email = Column(String)                 # email
    passport = Column(String)              # паспорт

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)          # для юр.лиц – наименование, для физ.лиц – ФИО
    type = Column(SAEnum(CustomerType), default=CustomerType.LEGAL)
    phone = Column(String)
    legal_address = Column(String)
    postal_address = Column(String)                # почтовый адрес
    inn = Column(String)
    bik = Column(String)
    kpp = Column(String)
    account_number = Column(String)
    corr_account = Column(String)                  # корр. счёт
    bank_name = Column(String)
    email = Column(String)                         # авторизованный адрес

    contracts = relationship("Contract", back_populates="customer")
    acts = relationship("Act", back_populates="customer")

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float)
    status = Column(SAEnum(ContractStatus), default=ContractStatus.ACTIVE)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer = relationship("Customer", back_populates="contracts")
    cheques = relationship("Cheque", back_populates="contract")
    acts = relationship("Act", back_populates="contract")
    file_path = Column(String)                     # путь к файлу договора

class Cheque(Base):
    __tablename__ = "cheques"
    id = Column(Integer, primary_key=True, index=True)
    link = Column(String)
    file_path = Column(String, nullable=True)
    date = Column(Date)
    amount = Column(Float)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    contract = relationship("Contract", back_populates="cheques")
    act_id = Column(Integer, ForeignKey("acts.id"), nullable=True)   # связь с актом
    act = relationship("Act", back_populates="cheques")

class Act(Base):
    __tablename__ = "acts"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(SAEnum(ActStatus), default=ActStatus.EMPTY)
    pdf_path = Column(String, nullable=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)  # теперь необязательно
    contract = relationship("Contract", back_populates="acts")
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True) # для актов без договора
    customer = relationship("Customer", back_populates="acts")
    services = relationship("ServiceItem", back_populates="act", cascade="all, delete-orphan")
    cheques = relationship("Cheque", back_populates="act")

class ServiceItem(Base):
    __tablename__ = "service_items"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1)
    unit_price = Column(Float, default=0)
    act_id = Column(Integer, ForeignKey("acts.id"))
    act = relationship("Act", back_populates="services")