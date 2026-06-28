import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from routers import auth, accounts, transactions, currency, charts, reports, csv_import

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables!")

app = FastAPI()

# ==================== MIDDLEWARE ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=86400,
    session_cookie="user_session",
    same_site="lax",
    https_only=True,
)


@app.middleware("http")
async def debug_session_middleware(request: Request, call_next):
    print(f"\n{'=' * 60}")
    print(f"📥 REQUEST: {request.method} {request.url.path}")
    print(f"🍪 Incoming Cookies: {request.cookies}")
    response = await call_next(request)
    print(f"📤 RESPONSE: {response.status_code}")
    print(f"🍪 Set-Cookie: {response.headers.get('set-cookie', 'NONE')}")
    print(f"{'=' * 60}\n")
    return response


# ==================== STATIC FILES ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")),
    name="static"
)

# ==================== PAGE ROUTES ====================

@app.get("/")
async def index_page():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "templates", "index.html"))


@app.get("/dashboard")
async def dashboard_page(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=302)
    return FileResponse(os.path.join(BASE_DIR, "frontend", "templates", "dashboard.html"))


@app.get("/accounts.html")
async def accounts_page():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "templates", "account.html"))


@app.get("/transactions.html")
async def transactions_page():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "templates", "transaction.html"))


@app.get("/import.html")
async def import_page():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "templates", "csv.html"))


@app.get("/reports.html")
async def reports_page():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "templates", "reports.html"))


# ==================== ROUTERS ====================

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(currency.router)
app.include_router(charts.router)
app.include_router(reports.router)
app.include_router(csv_import.router)
