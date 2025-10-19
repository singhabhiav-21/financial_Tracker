import requests

url = f"https://api.exchangerate-api.com/v4/latest/USD"
response = requests.get(url, timeout=10)
data = response.json()
base_currency = data['base']

rates = {
    base_currency: 1.0,
    'SEK': data['rates'].get('SEK'),
    'INR': data['rates'].get('INR')
}
multiplier_exchange = []


def add_exchangeRate(currency1, currency2):
    new_url = f"{url.rsplit('/', 1)[0]}/{currency1}"
    try:
        response = requests.get(new_url, timeout=10)
        data = response.json()

        base = data['base']
        rates[base] = 1.0

        if currency2 in data['rates']:
            rates[currency2] = data['rates'][currency2]
            rate = data['rates'][currency2]

            if rate not in multiplier_exchange:
                multiplier_exchange.append(rate)

            if len(multiplier_exchange) > 5:
                multiplier_exchange.pop(0)
            return rate
        else:
            print(f"Currency {currency2} not found!")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def calculate_currency(amount: int):
    if not multiplier_exchange:
        print("No exchange rates available!")
        return None
    return f"{multiplier_exchange[-1] * amount:.3f}"








