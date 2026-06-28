from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from dependencies import get_current_user
from models.transaction_models import TransactionCreate, TransactionUpdate
from databaseDAO.transaction.transaction_DAO import (
    register_transaction, delete_transaction, update_transaction,
    get_transaction, get_all_transactions
)

router = APIRouter(prefix="/transactions")


@router.post("")
async def create_transaction(data: TransactionCreate, current_user_id: int = Depends(get_current_user)):
    ok = await run_in_threadpool(
        register_transaction, current_user_id, data.category_id, data.name,
        data.amount, data.description, data.transaction_date, data.balance
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Transaction failed")
    return {"success": True}


@router.get("")
async def get_transactions(current_user_id: int = Depends(get_current_user)):
    return await run_in_threadpool(get_all_transactions, current_user_id)


@router.get("/{transaction_id}")
async def get_transaction_endpoint(transaction_id: int, current_user_id: int = Depends(get_current_user)):
    tx = await run_in_threadpool(get_transaction, transaction_id, current_user_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.put("/{transaction_id}")
async def update_transaction_endpoint(
    transaction_id: int,
    data: TransactionUpdate,
    current_user_id: int = Depends(get_current_user)
):
    ok = await run_in_threadpool(
        update_transaction, transaction_id, current_user_id,
        data.category_id, data.name, data.amount, data.description
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Update failed")
    return {"success": True}


@router.delete("/{transaction_id}")
async def delete_transaction_endpoint(transaction_id: int, current_user_id: int = Depends(get_current_user)):
    ok = await run_in_threadpool(delete_transaction, transaction_id, current_user_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Delete failed")
    return {"success": True}