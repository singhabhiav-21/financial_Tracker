import unittest
from unittest.mock import patch

from Visuals.ExchangeRates import ExchangeRates


class Test_exchangeRate(unittest.TestCase):

    def test_currency_conversion_accuracy(self):
        exchanger = ExchangeRates()
        ans = exchanger.convert(amount=100, from_currency='USD', to_currency='USD')
        self.assertEqual(ans, 100)

    @patch('Visuals.ExchangeRates.ExchangeRates.get_rates')
    def test_normal_conversion(self, mock_get_rates):
        exchanger = ExchangeRates()
        mock_get_rates.return_value = {"USD": 10.0}
        ans = exchanger.convert(amount=100, to_currency='SEK', from_currency='USD')
        self.assertEqual(ans, 10)

    @patch('Visuals.ExchangeRates.ExchangeRates.get_rates')
    def test_abnormal_currency(self, mock_get_rates):
        exchanger = ExchangeRates()
        mock_get_rates.return_value = {}
        ans = exchanger.convert(amount=100, to_currency='USD', from_currency='IDK')
        self.assertEqual(ans, 100)
