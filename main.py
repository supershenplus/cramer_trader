import re
import time
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from top_secret import API_KEY, API_SECRET

# todo: populate both final_short_stocks and final_long_stocks before placing any orders so you can remove any
#  duplicate/non active/non shortable picks all at once instead of each time placing an order,
#  beautify print statements, add more account functionality/control over orders, add requirements.txt, gitignore file

# selenium configurations, including automated chromedriver install/update/verification
op = webdriver.ChromeOptions()
op.add_argument('--headless')
chromedriver_autoinstaller.install()
page = webdriver.Chrome(options=op)
# alpaca markets API is used to place orders linked to our paper trading account
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
account = trading_client.get_account()

print(
    "--------------------------" "\n      cramerTrader" "\n--------------------------"
)

# where we can find mr.cramers stock picks
page.get("https://madmoney.thestreet.com/screener/index.cfm")


# defining functions that press enter, up arrow, and down arrow keys in browser
def key_enter():
    webdriver.ActionChains(page).key_down(Keys.ENTER).perform()


def key_up():
    webdriver.ActionChains(page).key_down(Keys.UP).perform()


def key_down():
    webdriver.ActionChains(page).key_down(Keys.DOWN).perform()


# change date range to last quarters picks
change_date = page.find_element(By.ID, "airdate")
change_date.click()
for _ in range(1):
    key_up()
    time.sleep(0.1)
key_enter()

# change to SELL picks
change_sell = page.find_element(By.ID, "called")
time.sleep(1)
change_sell.click()
for _ in range(5):
    key_down()
    time.sleep(0.1)
key_enter()

# displays up to 500 different picks, which should be more than enough for the time period we are using
page.get(
    "https://madmoney.thestreet.com/screener/index.cfm?showview=stocks&showrows=500"
)

# grabs cramers short picks, tickers are returned as "(EXAMPLE)" so the regex expression essentially looks for the value
# inside of two parenthesis "()", final_short_stocks then makes sure that it consolidates any duplicate tickers so that
# we do not order more than one of each stock
get_shorts = page.find_element(By.ID, "stockTable").text
print("Found stocks that Cramer was SHORT on last quarter!")
short_stocks = re.findall(r"\(([^)]+)\)", get_shorts)
final_short_stocks = list(dict.fromkeys(short_stocks))
# manually removing these stocks since the algo will fail at line "if not trading_client.get_asset(stock).tradeable:"
# reaching out to alpaca community for further support on this issue
final_short_stocks.remove("FB")
print(final_short_stocks)
print("Opening LONG positions on these stocks...")

# long order logic, also checks if the stock is tradeable on alpaca
not_tradeable = []
for stock in final_short_stocks:
    market_buy = MarketOrderRequest(
        symbol=stock, qty=1, side=OrderSide.BUY, time_in_force=TimeInForce.GTC
    )
    if not trading_client.get_asset(stock).tradable:
        print(stock, " ", trading_client.get_asset(stock).status, ", not purchasable")
    else:
        trading_client.submit_order(order_data=market_buy)
        print("Order for ", market_buy.symbol, " placed!")

# change to cramers BUY picks, still within the same timeframe
change_buy = page.find_element(By.ID, "called")
time.sleep(1)
change_buy.click()
for _ in range(4):
    key_up()
    time.sleep(.1)
key_enter()

# follows the same logic for finding cramers long picks, as it does for the short picks
get_longs = page.find_element(By.ID, "stockTable").text
print("\nFound stocks that Cramer was LONG on last quarter!")
long_stocks = re.findall(r"\(([^)]+)\)", get_longs)
final_long_stocks = list(dict.fromkeys(long_stocks))
final_long_stocks.remove("ELY")
final_long_stocks.remove("FB")

# check stocks to see if they are shortable in alpaca, if not they are removed from the list
not_shortable = []
for stock in final_long_stocks:
    if not trading_client.get_asset(stock).shortable:
        not_shortable.append(stock)
for stock in final_long_stocks:
    if stock in not_shortable:
        final_long_stocks.remove(stock)
        print("Stock not shortable: ", stock, "removing from SHORT list")

# cancels orders for stocks that have both buy and sell indicators
duplicate_order = []
for stock in final_short_stocks:
    if stock in final_long_stocks:
        duplicate_order.append(stock)
for stock in final_long_stocks:
    if stock in duplicate_order:
        final_long_stocks.remove(stock)
        print(stock, " already has a Buy order, cancelling both Buy and Sell order")

# short order logic, also checks if the stock is tradeable on alpaca
for stock in final_long_stocks:
    print(stock)
    market_sell = MarketOrderRequest(
        symbol=stock, qty=1, side=OrderSide.SELL, time_in_force=TimeInForce.GTC
    )
    if not trading_client.get_asset(stock).tradable:
        print(stock, " ", trading_client.get_asset(stock).status, ", not purchasable")
    else:
        print("Short order for ", market_sell.symbol, " placed!")
        trading_client.submit_order(order_data=market_sell)

print("\nBuying complete.")

