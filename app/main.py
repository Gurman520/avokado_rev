from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from app.database import engine, Base
from app.routers import auth_router, profile_router, customer_router, contract_router, cheque_router, act_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Договоры и акты самозанятого")

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
async def root():
    return RedirectResponse(url="/profile")