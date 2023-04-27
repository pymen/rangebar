from src.helpers.fiat_convert import CryptoToFiatConverter
from src.helpers.util import get_unix_epoch_time_ms
from src.settings import get_settings
from binance.um_futures import UMFutures as Client


def test_crypto_to_fiat():
    converter_instance = CryptoToFiatConverter()
    res = converter_instance.convert_amount(0.001, "BTC", "USD")
    print(f'1 BTC is {res} USD')

def test_get_price():
    converter_instance = CryptoToFiatConverter()
    usdt_price_usd = converter_instance.get_price("USDT", "USD")
    btc_price_usd = converter_instance.get_price("BTC", "USD")
    print(f'USDT price in USD: {usdt_price_usd}, BTC price in USD: {btc_price_usd}')

def test_get_balance():
    settings = get_settings('bi')
    client = Client(key=settings['key'], secret=settings['secret'], base_url=settings['base_url'])
    dict_list: list[dict[str, str]] = client.balance() # type: ignore
    usdt_dist: dict[str, str] = next((x for x in dict_list if x['asset'] == 'USDT'))
    balance = float(usdt_dist['availableBalance'])
    print(f'get_balance: usdt availableBalance: {balance}')
    percent = 0.02
    usdt_quantity = balance * percent
    print(f'get_balance: usdt quantity: {usdt_quantity}')


