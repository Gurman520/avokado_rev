from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.database import engine, Base, SessionLocal
from app.models import Customer, Contract, Cheque, Act, ContractStatus
from app.auth import get_user_from_cookie
from app.template_config import templates
from app.routers import auth_router, profile_router, customer_router, contract_router, cheque_router, act_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Учёт договоров")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(customer_router.router)
app.include_router(contract_router.router)
app.include_router(cheque_router.router)
app.include_router(act_router.router)

@app.get("/")
async def dashboard(request: Request, user = Depends(get_user_from_cookie)):
    db = SessionLocal()
    stats = {
        "customers": db.query(Customer).count(),
        "contracts": db.query(Contract).count(),
        "active_contracts": db.query(Contract).filter(Contract.status == ContractStatus.ACTIVE).count(),
        "cheques": db.query(Cheque).count(),
        "acts": db.query(Act).count(),
    }
    # Сумма заработанного по каждому договору
    earned_rows = (
        db.query(Cheque.contract_id, func.sum(Cheque.amount))
        .group_by(Cheque.contract_id)
        .all()
    )
    earned_map = {cid: (amount or 0.0) for cid, amount in earned_rows}

    # Общая сумма заработка
    total_earned = sum(earned_map.values())

    recent_contracts = (
        db.query(Contract)
        .options(joinedload(Contract.customer))
        .order_by(Contract.id.desc())
        .limit(5)
        .all()
    )
    db.close()
    return templates.TemplateResponse(request, "dashboard.html", {
         "stats": stats,
        "recent_contracts": recent_contracts,
        "earned_map": earned_map,
        "total_earned": total_earned,
    })