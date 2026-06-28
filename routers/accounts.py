from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from dependencies import get_current_user
from models.account_models import AccountCreate, AccountUpdate, AccountDelete
from databaseDAO.Account.account_dao import (
    addAccount, delete_account, update_account,
    get_all_accounts, get_account
)

router = APIRouter(prefix="/accounts")


@router.post("")
async def create_account(data: AccountCreate, current_user_id: int = Depends(get_current_user)):
    ok = await run_in_threadpool(
        addAccount, current_user_id, data.name, data.type,
        data.balance, data.currency, data.platform_name
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Account creation failed")
    return {"success": True}


@router.get("")
async def get_accounts(current_user_id: int = Depends(get_current_user)):
    return await run_in_threadpool(get_all_accounts, current_user_id)


@router.get("/{account_id}")
async def get_account_by_id(account_id: int, current_user_id: int = Depends(get_current_user)):
    account = await run_in_threadpool(get_account, account_id, current_user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or access denied")
    return account


@router.put("/{account_id}")
async def update_account_endpoint(
    account_id: int,
    data: AccountUpdate,
    current_user_id: int = Depends(get_current_user)
):
    ok = await run_in_threadpool(
        update_account, account_id, current_user_id,
        data.name, data.accountType, data.balance, data.currency, data.platform_name
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Update failed")
    return {"success": True}


@router.delete("/{account_id}")
async def delete_account_endpoint(
    account_id: int,
    data: AccountDelete,
    current_user_id: int = Depends(get_current_user)
):
    ok = await run_in_threadpool(delete_account, current_user_id, account_id, data.password)
    if not ok:
        raise HTTPException(status_code=400, detail="Delete failed")
    return {"success": True, "message": "Account deleted successfully"}