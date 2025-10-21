from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from financial_Tracker.databaseDAO.sqlConnector import get_connection

from financial_Tracker.databaseDAO.sqlConnector import get_connection

conn = get_connection()
cursor = conn.cursor


def get_data(user_id, month):
    query = """
    SELECT transaction_date,
        amount,
        name,
        description
    FROM transactions
    WHERE user_id = %s AND DATE_FORMAT(transaction_date, '%Y-%m') = %s
    ORDER BY transaction_date
    """
    cursor.execute(query, (user_id, month))
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    if not result:
        print("The user has no data!(visual)")
        return False

    df = pd.DataFrame(result, columns=['transaction_date', 'name', 'amount', 'description'])
    return df


def get_spent(df):
    daily_spending = df.groupby('transaction_date')['amount'].sum().reset_index()
    sorted_df = daily_spending.sort_values(by='amount', ascending=False)
    max_row = sorted_df.iloc[0]
    formatted_max = {
        'transaction_date': max_row['transaction_date'],
        'name': max_row['name'],
        'amount': max_row['amount']
    }
    return formatted_max


def get_all_transactions(df):
    all_transactions = df.sort_values(by='transaction_date', ascending=True)
    formatted_all_transaction = {
        'transaction_date': all_transactions['transaction_date'],
        'name': all_transactions['name'],
        'amount': all_transactions['amount'],
        'description': all_transactions['description']
    }
    return formatted_all_transaction


def get_monthly_summary(df):
    all_data = {
        'total': df['amount'].sum(),
        'average': df['amount'].mean(),
        'count': len(df),
        'min': df['amount'].min(),
        'max': df['amount'].max()
    }
    return all_data


def prepared_for_chart(df):
    daily_spending = df.groupby('transaction_date')['amount'].sum().reset_index()
    daily_spending = daily_spending.sort_values('transaction_date')

    return {
        'amounts': daily_spending['amount'].to_list(),
        'days':  [d.day for d in daily_spending['transaction_date']],
        'dates': list(daily_spending['transaction_date'])
    }

def create_highest_day_section(max_day_data, styles):
    elements = []

    elements.append(Paragraph("Highest Spending Day", styles['Heading2']))
    elements.append(Spacer(1, 6))

    table_data = [
        ['Date', 'Total Amount'],
        [str(max_day_data['date']), f"${max_day_data['amount']:.2f}"]
    ]

    table = Table(table_data, colWidths=[200, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))
    return elements