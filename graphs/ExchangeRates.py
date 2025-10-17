import requests
import os

url = f"https://api.exchangerate-api.com/v4/latest/USD"
response = requests.get(url, timeout=10)
data = response.json()
base_currency = data['base']

rates = {
    base_currency: 1.0,
    'SEK': data['rates'].get('SEK'),
    'INR': data['rates'].get('INR')
}


def add_exchangeRate(currency1, currency2):
    new_url = f"{url.rsplit('/', 1)[0]}/{currency1}"
    try:
        response = requests.get(new_url, timeout=10)
        data = response.json()

        base = data['base']
        rates[base] = 1.0

        if currency2 in data['rates']:
            rates[currency2] = data['rates'][currency2]
            print("user")
            return data['rates'][currency2]
        else:
            print(f"Currency {currency2} not found!")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def calculate_currency(amount: int, base, target):
    multiplier = add_exchangeRate(base, target)
    return f"{multiplier * amount}"


base = "SEK"

target = "INR"
print(add_exchangeRate(base, target))
print(calculate_currency(21, base,target))



