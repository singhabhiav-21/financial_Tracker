from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import date
import tempfile
import os
from pathlib import Path

# DAO imports
from databaseDAO.userDAO import logIn, register, update_userinfo, update_password
from databaseDAO.Account.account_dao import (
    addAccount, delete_account, update_account,
    add_money, transfer_money
)
from databaseDAO.transaction.transaction_DAO import (
    register_transaction, delete_transaction, update_transaction,
    get_transaction
)
from databaseDAO.transaction.importcsv import bankImporter

app = FastAPI()

# ==================== CORS ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== STATIC FILES ====================

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


# ==================== PAGE ROUTES ====================
# These are REQUIRED for your sidebar navigation

@app.get("/")
async def index_page():
    return FileResponse("frontend/templates/index.html")


@app.get("/dashboard")
async def dashboard_redirect():
    return RedirectResponse(url="/dashboard.html")


@app.get("/dashboard.html")
async def dashboard_page():
    return FileResponse("frontend/templates/dashboard.html")


@app.get("/accounts.html")
async def accounts_page():
    return FileResponse("frontend/templates/account.html")


@app.get("/transactions.html")
async def transactions_page():
    return FileResponse("frontend/templates/transaction.html")


@app.get("/import.html")
async def import_page():
    return FileResponse("frontend/templates/csv.html")


# ==================== USER MODELS ====================

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class UpdateUserRequest(BaseModel):
    email: str
    name: Optional[str] = None
    new_email: Optional[str] = None


class UpdatePasswordRequest(BaseModel):
    email: str
    old_password: str
    password: str
    re_password: str


# ==================== ACCOUNT MODELS ====================

class AccountCreate(BaseModel):
    user_id: int
    name: str
    type: str
    balance: float
    currency: str = "USD"
    platform_name: Optional[str] = None


class AccountUpdate(BaseModel):
    user_id: int
    name: Optional[str] = None
    type: Optional[str] = None
    balance: Optional[float] = None
    currency: Optional[str] = None
    platform_name: Optional[str] = None


class AccountDelete(BaseModel):
    password: str


class AddMoney(BaseModel):
    user_id: int
    amount: float


class MoneyTransfer(BaseModel):
    user_id: int
    from_account_id: int
    to_account_id: int
    amount: float


# ==================== TRANSACTION MODELS ====================

class TransactionCreate(BaseModel):
    user_id: int
    category_id: int
    name: str
    amount: float
    description: Optional[str] = None
    transaction_date: Optional[date] = None
    balance: Optional[float] = None


class TransactionUpdate(BaseModel):
    user_id: int
    category_id: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None


# ==================== AUTH ENDPOINTS ====================

@app.post("/login")
async def login_endpoint(data: LoginRequest):
    success, user_id = logIn(data.email, data.password)
    if not success:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "success": True,
        "user_id": user_id,
        "message": "Login successful"
    }


@app.post("/register")
async def register_endpoint(data: RegisterRequest):
    result = register(data.name, data.email, data.password)
    if not result:
        raise HTTPException(status_code=400, detail="Registration failed")

    return {"success": True, "message": "User registered successfully"}


@app.put("/update-user")
async def update_user_endpoint(data: UpdateUserRequest):
    if not update_userinfo(data.email, data.name, data.new_email):
        raise HTTPException(status_code=400, detail="Update failed")

    return {"success": True}


@app.put("/update-password")
async def update_password_endpoint(data: UpdatePasswordRequest):
    if not update_password(
            data.email, data.old_password, data.password, data.re_password
    ):
        raise HTTPException(status_code=400, detail="Password update failed")

    return {"success": True}


# ==================== ACCOUNT ENDPOINTS ====================

@app.post("/accounts")
async def create_account(account: AccountCreate):
    if not addAccount(
            userid=account.user_id,
            name=account.name,
            type=account.type,
            balance=account.balance,
            currency=account.currency,
            platform_name=account.platform_name
    ):
        raise HTTPException(status_code=400, detail="Account creation failed")

    return {"success": True}


@app.get("/accounts")
async def get_accounts(user_id: int):
    from databaseDAO.sqlConnector import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM account WHERE user_id=%s", (user_id,))
    rows = cursor.fetchall()

    if not rows:
        return []

    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


@app.put("/accounts/{account_id}")
async def update_account_endpoint(account_id: int, data: AccountUpdate):
    if not update_account(
            account_id,
            data.user_id,
            data.name,
            data.type,
            data.balance,
            data.currency,
            data.platform_name
    ):
        raise HTTPException(status_code=400, detail="Update failed")

    return {"success": True}


@app.delete("/accounts/{account_id}")
async def delete_account_endpoint(account_id: int, data: AccountDelete):
    if not delete_account(account_id, data.password):
        raise HTTPException(status_code=400, detail="Delete failed")

    return {"success": True}


@app.post("/accounts/{account_id}/add-money")
async def add_money_endpoint(account_id: int, data: AddMoney):
    if not add_money(data.user_id, account_id, int(data.amount)):
        raise HTTPException(status_code=400, detail="Add money failed")

    return {"success": True}


@app.post("/accounts/transfer")
async def transfer_money_endpoint(data: MoneyTransfer):
    if not transfer_money(
            data.user_id,
            data.from_account_id,
            data.to_account_id,
            int(data.amount)
    ):
        raise HTTPException(status_code=400, detail="Transfer failed")

    return {"success": True}


# ==================== TRANSACTION ENDPOINTS ====================

@app.post("/transactions")
async def create_transaction(transaction: TransactionCreate):
    if not register_transaction(
            transaction.user_id,
            transaction.category_id,
            transaction.name,
            transaction.amount,
            transaction.description,
            transaction.transaction_date,
            transaction.balance
    ):
        raise HTTPException(status_code=400, detail="Transaction failed")

    return {"success": True}


@app.get("/transactions")
async def get_transactions(user_id: int):
    from databaseDAO.sqlConnector import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM transactions WHERE user_id=%s ORDER BY transaction_date DESC",
        (user_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        return []

    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


@app.get("/transactions/{transaction_id}")
async def get_transaction_endpoint(transaction_id: int, user_id: int):
    tx = get_transaction(transaction_id, user_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return tx


@app.put("/transactions/{transaction_id}")
async def update_transaction_endpoint(transaction_id: int, data: TransactionUpdate):
    if not update_transaction(
            transaction_id,
            data.user_id,
            data.category_id,
            data.name,
            data.amount,
            data.description
    ):
        raise HTTPException(status_code=400, detail="Update failed")

    return {"success": True}


@app.delete("/transactions/{transaction_id}")
async def delete_transaction_endpoint(transaction_id: int, user_id: int):
    if not delete_transaction(transaction_id, user_id):
        raise HTTPException(status_code=400, detail="Delete failed")

    return {"success": True}


# ==================== CSV IMPORT ENDPOINT ====================

# Security constants for file upload
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.csv'}
ALLOWED_MIME_TYPES = {'text/csv', 'application/vnd.ms-excel', 'text/plain', 'application/csv'}


def validate_file_security(file: UploadFile) -> tuple[bool, str]:
    """
    Validates file for security issues
    Returns: (is_valid, error_message)
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, "Invalid file type. Only CSV files allowed."

    # Check MIME type (some browsers don't send MIME type, so allow empty)
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid MIME type: {file.content_type}"

    # Check filename for suspicious patterns
    suspicious_chars = ['..', '\0', '<', '>', ':', '"', '|', '?', '*']
    if any(char in file.filename for char in suspicious_chars):
        return False, "Invalid filename format"

    # Check filename length
    if len(file.filename) > 255:
        return False, "Filename too long"

    return True, ""


@app.post("/import-csv")
async def import_csv_transactions(
        file: UploadFile = File(...),
        user_id: int = Form(...)
):
    """
    Endpoint to import transactions from CSV file

    Security features:
    - File type validation
    - File size limits
    - Temporary file handling
    - Automatic cleanup
    """

    # Validate user_id
    if not user_id or user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # Security validation
    is_valid, error_msg = validate_file_security(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    temp_file_path = None
    try:
        # Read file content
        content = await file.read()

        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.1f} MB"
            )

        # Check for empty file
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")

        # Additional security: Check for null bytes
        if b'\x00' in content:
            raise HTTPException(status_code=400, detail="File contains invalid characters")

        # Decode and validate CSV structure
        try:
            text_content = content.decode('utf-8-sig')  # Handle BOM
        except UnicodeDecodeError:
            try:
                text_content = content.decode('latin-1')  # Fallback encoding
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to decode file. Please ensure it's a valid CSV."
                )

        # Validate CSV has required columns
        lines = text_content.split('\n')[:2]  # Check first 2 lines
        if len(lines) < 2:
            raise HTTPException(status_code=400, detail="CSV file is too short or empty")

        header = lines[0].lower()
        required_cols = ['value date', 'text', 'amount']

        if not all(col in header for col in required_cols):
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns. Expected: {', '.join(required_cols)}"
            )


        # Create secure temporary file
        with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.csv',
                delete=False,
                encoding='utf-8'
        ) as temp_file:
            temp_file.write(text_content)
            temp_file_path = temp_file.name

        # Process the file using bankImporter
        importer = bankImporter(user_id=user_id, default_category_id=1)
        result = importer.import_csv(temp_file_path)

        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        # Return results
        return JSONResponse(
            status_code=200,
            content={
                "message": "Import completed successfully",
                "imported": importer.imported_count,
                "duplicates": importer.duplicate_count,
                "total": importer.imported_count + importer.duplicate_count,
                "user_id": user_id
            }
        )

    except HTTPException:
        # Clean up temp file on HTTP exceptions
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise

    except Exception as e:
        # Clean up temp file on any other exception
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass

        print(f"Error processing CSV import: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Ensure file is closed
        await file.close()