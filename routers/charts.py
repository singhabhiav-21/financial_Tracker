from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_current_user
from Visuals.ExchangeRates import get_currency_converter
from Visuals.BarChart import weekly_expenses, incoming_funds, outgoing_funds
import pandas as pd

router = APIRouter(prefix="/api")


@router.get("/weekly-chart")
async def get_weekly_chart_data(
    current_user_id: int = Depends(get_current_user),
    weeks: int = 8,
    base_currency: str = "USD"
):
    try:
        transactions = weekly_expenses(current_user_id, weeks)

        if not transactions:
            return {
                'success': False,
                'error': 'No transactions found for this user',
                'user_id': current_user_id,
                'weeks': weeks
            }

        df = pd.DataFrame(transactions, columns=["Date", "Amount"])
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)

        weekly = df.resample('W-MON').agg({'Amount': [incoming_funds, outgoing_funds]})
        weekly = weekly.reset_index()
        weekly.columns = ['Date', 'Income', 'Expenses']
        weekly['Net'] = weekly['Income'] - weekly['Expenses']

        converter = get_currency_converter()
        needs_conversion = base_currency != 'SEK'

        weekly_data = []
        for _, row in weekly.iterrows():
            income = float(row['Income'])
            expenses = float(row['Expenses'])
            net = float(row['Net'])

            if needs_conversion:
                income = converter.convert(income, 'SEK', base_currency)
                expenses = converter.convert(expenses, 'SEK', base_currency)
                net = converter.convert(net, 'SEK', base_currency)

            weekly_data.append({
                'date': row['Date'].strftime('%Y-%m-%d'),
                'income': round(income, 2),
                'expenses': round(expenses, 2),
                'net': round(net, 2)
            })

        total_income = sum(w['income'] for w in weekly_data)
        total_expenses = sum(w['expenses'] for w in weekly_data)

        return {
            'success': True,
            'user_id': current_user_id,
            'weeks': weeks,
            'base_currency': base_currency,
            'source_currency': 'SEK',
            'conversion_applied': needs_conversion,
            'weekly_data': weekly_data,
            'summary': {
                'total_income': round(total_income, 2),
                'total_expenses': round(total_expenses, 2),
                'total_net': round(total_income - total_expenses, 2),
                'average_weekly_income': round(total_income / len(weekly_data), 2) if weekly_data else 0,
                'average_weekly_expenses': round(total_expenses / len(weekly_data), 2) if weekly_data else 0
            },
            'total_weeks': len(weekly_data),
            'date_range': {
                'start': weekly_data[0]['date'] if weekly_data else None,
                'end': weekly_data[-1]['date'] if weekly_data else None
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))