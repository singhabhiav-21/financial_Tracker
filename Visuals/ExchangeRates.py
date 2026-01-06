import requests
from datetime import datetime, timedelta
from typing import Dict, List


class ExchangeRates:

    def __init__(self):
        self.api_url = "https://api.exchangerate-api.com/v4/latest"
        self.cache = {}
        self.cache_time = None
        self.cache_hours = 12  # Refresh every 12 hours

    def get_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """
        Get exchange rates from API with simple caching

        Args:
            base_currency: Base currency (e.g., "USD")

        Returns:
            Dictionary of rates like {"EUR": 0.92, "SEK": 10.87, ...}
            Meaning: 1 base_currency = X other_currency
            Example: If base is USD, then rates["SEK"] = 10.87 means 1 USD = 10.87 SEK
        """
        # Check if cache is still valid
        if self._is_cache_valid() and self.cache.get('base') == base_currency:
            print(f"✅ Using cached rates for {base_currency}")
            return self.cache.get('rates', {})

        # Fetch new rates
        try:
            url = f"{self.api_url}/{base_currency}"
            print(f"🌐 Fetching rates from {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            rates = data['rates']
            rates[base_currency] = 1.0  # Add base currency

            # Update cache with base currency info
            self.cache = {
                'rates': rates,
                'base': base_currency
            }
            self.cache_time = datetime.now()

            print(f"✅ Got {len(rates)} exchange rates for base {base_currency}")
            print(f"   Sample: 1 {base_currency} = {rates.get('SEK', 'N/A')} SEK, {rates.get('EUR', 'N/A')} EUR")
            return rates

        except Exception as e:
            print(f"❌ Error getting rates: {e}")
            # If cache exists, use it even if old
            if self.cache and self.cache.get('rates'):
                print("⚠️ Using old cached rates")
                return self.cache.get('rates', {})
            # Otherwise return empty dict
            return {}

    def _is_cache_valid(self) -> bool:
        """Check if cache is less than 12 hours old"""
        if not self.cache or not self.cache_time:
            return False

        age = datetime.now() - self.cache_time
        return age < timedelta(hours=self.cache_hours)

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency (e.g., "SEK")
            to_currency: Target currency (e.g., "USD")

        Returns:
            Converted amount

        Logic:
            Step 1: Get rates where to_currency is the base
                   This gives us: 1 to_currency = X from_currency
            Step 2: Divide amount by the rate
                   amount (in from_currency) / rate = amount (in to_currency)

        Example:
            Convert 100 SEK to USD:
            - Get rates with base=USD: {"SEK": 10.87} (1 USD = 10.87 SEK)
            - Calculate: 100 SEK / 10.87 = 9.20 USD ✓
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Same currency = no conversion
        if from_currency == to_currency:
            print(f"ℹ️ Same currency ({from_currency}), no conversion needed")
            return round(amount, 2)

        # Get rates with to_currency as base
        rates = self.get_rates(to_currency)

        if not rates:
            print(f"❌ No rates available, returning original amount")
            return amount

        # Get the rate for from_currency
        rate = rates.get(from_currency)

        if rate is None:
            print(f"❌ Currency {from_currency} not found in rates")
            return amount

        # Convert: amount / rate
        converted = amount / rate

        print(f"💱 Convert: {amount:.2f} {from_currency} → {converted:.2f} {to_currency} (rate: {rate:.4f})")

        return round(converted, 2)

    def convert_accounts(self, accounts: List[Dict], base_currency: str = "USD") -> Dict:
        """
        Convert all accounts to one currency and calculate total

        Args:
            accounts: List of account dicts with 'account_balance' and 'currency'
            base_currency: Target currency (e.g., "USD")

        Returns:
            Dictionary with total and converted accounts
        """
        print(f"\n{'=' * 60}")
        print(f"CONVERTING ACCOUNTS TO {base_currency}")
        print(f"{'=' * 60}")

        rates = self.get_rates(base_currency)

        if not rates:
            return {
                'success': False,
                'error': 'Could not fetch exchange rates',
                'total_balance': 0,
                'base_currency': base_currency,
                'accounts': []
            }

        converted_accounts = []
        total_balance = 0.0

        for account in accounts:
            # Get original values
            original_balance = float(account.get('account_balance', 0))
            original_currency = account.get('currency', 'USD').upper()

            print(f"\n📊 Account: {account.get('account_name')}")
            print(f"   Original: {original_balance:.2f} {original_currency}")

            # Convert to base currency
            converted_balance = self.convert(original_balance, original_currency, base_currency)
            total_balance += converted_balance

            print(f"   Converted: {converted_balance:.2f} {base_currency}")

            # Create converted account data
            converted_account = {
                'account_id': account.get('account_id'),
                'account_name': account.get('account_name'),
                'account_type': account.get('account_type'),
                'platform_name': account.get('platform_name'),
                'original_balance': original_balance,
                'original_currency': original_currency,
                'converted_balance': converted_balance,
                'conversion_rate': rates.get(original_currency, 1.0)
            }
            converted_accounts.append(converted_account)

        print(f"\n{'=' * 60}")
        print(f"✅ TOTAL: {total_balance:.2f} {base_currency}")
        print(f"{'=' * 60}\n")

        return {
            'success': True,
            'total_balance': round(total_balance, 2),
            'base_currency': base_currency,
            'account_count': len(accounts),
            'accounts': converted_accounts,
            'timestamp': datetime.now().isoformat()
        }


# ==================== SINGLETON PATTERN ====================
_currency_converter_instance = None


def get_currency_converter() -> ExchangeRates:
    """
    Get the global currency converter instance (Singleton Pattern)
    """
    global _currency_converter_instance

    if _currency_converter_instance is None:
        print("🆕 Creating new currency converter instance")
        _currency_converter_instance = ExchangeRates()
    else:
        print("♻️ Reusing existing currency converter instance")

    return _currency_converter_instance


# Testing
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTING CURRENCY CONVERTER")
    print("=" * 80)

    # Test with your actual account values
    sample_accounts = [
        {
            'account_id': 1,
            'account_name': 'MyACCOUNT1',
            'account_type': 'current',
            'account_balance': 5009.81,
            'currency': 'SEK',
            'platform_name': 'seb'
        },
        {
            'account_id': 2,
            'account_name': 'Navimumbai',
            'account_type': 'fixed deposit',
            'account_balance': 1023.00,
            'currency': 'USD',
            'platform_name': 'Chase'
        },
        {
            'account_id': 3,
            'account_name': 'Navimumbai',
            'account_type': 'savings',
            'account_balance': 210201.00,
            'currency': 'INR',
            'platform_name': 'SBI'
        },
        {
            'account_id': 4,
            'account_name': 'aldhjöf',
            'account_type': 'fixed deposit',
            'account_balance': 1000.00,
            'currency': 'EUR',
            'platform_name': 'SAS'
        }
    ]

    converter = get_currency_converter()

    # Test conversion to USD
    print("\n" + "=" * 80)
    print("TEST 1: Convert all accounts to USD")
    print("=" * 80)
    result_usd = converter.convert_accounts(sample_accounts, base_currency="USD")

    if result_usd['success']:
        print(f"\n✅ EXPECTED: ~$5,000 USD")
        print(f"✅ RESULT: ${result_usd['total_balance']:.2f} USD")

    # Test conversion to SEK
    print("\n" + "=" * 80)
    print("TEST 2: Convert all accounts to SEK")
    print("=" * 80)
    result_sek = converter.convert_accounts(sample_accounts, base_currency="SEK")

    if result_sek['success']:
        print(f"\n✅ EXPECTED: ~54,000 SEK")
        print(f"✅ RESULT: {result_sek['total_balance']:.2f} SEK")

    # Test conversion to GBP
    print("\n" + "=" * 80)
    print("TEST 3: Convert all accounts to GBP")
    print("=" * 80)
    result_gbp = converter.convert_accounts(sample_accounts, base_currency="GBP")

    if result_gbp['success']:
        print(f"\n✅ EXPECTED: ~£4,000 GBP")
        print(f"✅ RESULT: £{result_gbp['total_balance']:.2f} GBP")