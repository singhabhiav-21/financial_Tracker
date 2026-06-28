from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_current_user
from databaseDAO.Account.account_dao import get_all_accounts
from databaseDAO.transaction.transaction_DAO import get_all_transactions
from Visuals.ExchangeRates import get_currency_converter

router = APIRouter(prefix="/api/currency")


@router.get("/dashboard")
async def get_dashboard_converted(
    current_user_id: int = Depends(get_current_user),
    base_currency: str = "USD"
):
    accounts = get_all_accounts(current_user_id)
    transactions = get_all_transactions(current_user_id)
    converter = get_currency_converter()
    conversion_result = converter.convert_accounts(accounts, base_currency)

    if not conversion_result['success']:
        raise HTTPException(status_code=500, detail=conversion_result.get('error'))

    total_income = sum(float(t['amount']) for t in transactions if float(t['amount']) > 0)
    total_expenses = sum(abs(float(t['amount'])) for t in transactions if float(t['amount']) < 0)

    return {
        'success': True,
        'user_id': current_user_id,
        'base_currency': base_currency,
        'statistics': {
            'total_balance': conversion_result['total_balance'],
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'account_count': len(accounts)
        },
        'accounts': conversion_result['accounts'],
        'recent_transactions': transactions[:5],
        'timestamp': conversion_result['timestamp']
    }


@router.get("/accounts/converted")
async def get_accounts_converted(
    current_user_id: int = Depends(get_current_user),
    base_currency: str = "USD"
):
    accounts = get_all_accounts(current_user_id)
    converter = get_currency_converter()
    result = converter.convert_accounts(accounts, base_currency)
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error'))
    return result


@router.get("/rates")
async def get_exchange_rates(base_currency: str = "USD"):
    try:
        converter = get_currency_converter()
        rates = converter.get_rates(base_currency)
        if not rates:
            raise HTTPException(status_code=500, detail="Could not fetch rates")
        return {'success': True, 'base_currency': base_currency, 'rates': rates, 'count': len(rates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))