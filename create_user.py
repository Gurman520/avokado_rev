from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash

# Создаём все таблицы
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Проверим, нет ли уже пользователя
if db.query(User).filter(User.username == "admin").first():
    print("Пользователь admin уже существует")
else:
    user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="Сулима Роман Иванович",
        inn="123456789012",
        bik="044525225",
        kpp="771401001",
        account_number="40802810000000000001",
        bank_name="Сбербанк"
    )
    db.add(user)
    db.commit()
    print("Пользователь admin создан (пароль: admin123)")

db.close()