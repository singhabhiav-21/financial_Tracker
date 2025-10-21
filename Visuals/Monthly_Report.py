from reportlab.lib.pagesizes import letter
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from financial_Tracker.databaseDAO.sqlConnector import get_connection

conn = get_connection()
cursor = conn.cursor()


def get_data(user_id, month):
    if not user_exists(user_id):
        print(f"User with ID {user_id} does not exist!")
        return None

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

    if not result:
        print("The user has no data!(visual)")
        return None

    df = pd.DataFrame(result, columns=['transaction_date', 'amount' ,'name' , 'description'])
    return df


def user_exists(user_id):
    query = "SELECT 1 FROM users WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    return result is not None


def get_spent(df):
    daily_spending = df.groupby('transaction_date')['amount'].sum().reset_index()
    sorted_df = daily_spending.sort_values(by='amount', ascending=False)
    max_row = sorted_df.iloc[0]
    formatted_max = {
        'transaction_date': max_row['transaction_date'],
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
        'amounts': daily_spending['amount'].tolist(),
        'days': [d.day for d in daily_spending['transaction_date']],
        'dates': list(daily_spending['transaction_date'])
    }


def create_highest_day_section(max_day_data, styles):
    elements = []

    elements.append(Paragraph("Highest Spending Day", styles['Heading2']))
    elements.append(Spacer(1, 6))

    table_data = [
        ['Date', 'Total Amount'],
        [str(max_day_data['transaction_date']), f"SEK{max_day_data['amount']:.2f}"]
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


def create_chart_section(chart_data, styles):
    elements = []

    elements.append(Paragraph("Daily Spending Trend", styles['Heading2']))
    elements.append(Spacer(1, 12))

    drawing = Drawing(400, 200)
    lc = HorizontalLineChart()
    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = [tuple(float(x) for x in chart_data['amounts'])]
    lc.joinedLines = 1
    lc.lines[0].strokeColor = colors.HexColor('#E74C3C')
    lc.lines[0].strokeWidth = 2

    lc.categoryAxis.categoryNames = [str(d) for d in chart_data['days']]
    lc.categoryAxis.labels.fontSize = 8
    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = float(max(chart_data['amounts'])) * 1.1

    drawing.add(lc)
    elements.append(drawing)
    elements.append(Spacer(1, 20))
    return elements


def create_transaction_list_section(df, summary, styles):
    elements = []

    elements.append(Paragraph("Transaction List", styles['Heading2']))
    elements.append(Spacer(1, 12))

    summary_text = (
        f"Total Spending: SEK{summary['total']:.2f} | "
        f"Average Transaction: SEK{summary['average']:.2f} | "
        f"Total Transactions: {summary['count']}"
    )
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    table_data = [['Date', 'Name', 'Amount', 'Description']]

    for _, row in df.iterrows():
        table_data.append([
            str(row['transaction_date']),
            str(row['name'])[:20],
            f"SEK{row['amount']:.2f}",
            str(row['description'])[:30] if row['description'] else 'N/A'
        ])

    table = Table(table_data, colWidths=[80, 120, 80, 180])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    elements.append(table)
    return elements


def make_report(user_id, month, output_filename=None):
    if output_filename is None:
        output_filename = f'financial_report_{month}.pdf'

    df = get_data(user_id, month)
    if df is None:
        return False

    max_day = get_spent(df)
    chart_data = prepared_for_chart(df)
    summary = get_monthly_summary(df)

    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30
    )
    elements.append(Paragraph(f"Financial Report - {month}", title_style))
    elements.append(Spacer(1, 12))

    elements.extend(create_highest_day_section(max_day, styles))
    elements.extend(create_chart_section(chart_data, styles))
    elements.extend(create_transaction_list_section(df, summary, styles))

    doc.build(elements)
    print(f"Report generated successfully: {output_filename}")
    return True

make_report(user_id=52, month='2025-10')

