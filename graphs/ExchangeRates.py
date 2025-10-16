import requests
from dotenv import load_dotenv
import os


load_dotenv()
API_KEY = os.getenv("EXCHANGE_API_KEY")

url = f"https://api.exchangerate-api.com/v4/latest/SEK"
response = requests.get(url, timeout=10)
data = response.json()

rates = {
    'SEK': 1.0,  # USD is always 1 relative to itself
    'USD': data['rates']['USD'],
    'INR': data['rates']['INR']
}

print(rates)