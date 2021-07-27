from django.db.models import Count, Case, When, BooleanField, Value
from challenge.models import TSXStock, Holding, Transaction, Watchlist, WatchlistItem

from django.utils import timezone
from django.conf import settings
from . import utils
import requests
import json
import datetime


def get_market_summary(request):
    #
    # Get Market Summary for Canada
    #
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-summary"

    querystring = {"region": "CA"}
    headers = {
        'x-rapidapi-key': settings.X_RAPIDAPI_KEY,
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        # Deserialize the response to a python object
        json_data = json.loads(response.text)
        return json_data['marketSummaryAndSparkResponse']['result']
    else:
        return None


def get_news_headlines(request):
    #
    # Get the News Headlines for Canada
    #
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/list"
    querystring = {"region": "CA", "snippetCount": "10"}
    payload = "Pass in the value of uuids field returned right in this endpoint to load the next" \
              " page, or leave empty to load first page "
    headers = {
        'content-type': "text/plain",
        'x-rapidapi-key': "438c096415mshb0589791ceeff23p107e84jsnd9ed933221e3",
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    if response.status_code == 200:
        # Deserialize the response to a python object
        json_data = json.loads(response.text)
        return json_data['data']['main']['stream']
    else:
        return None


# def get_quotes(request, symbols):
#     #
#     # Make API calls to retreive quotes for securities of interest
#     #
#     sym_list = symbols
#
#     # If sym_list is empty, return None
#     if len(sym_list) == 0:
#         return None
#
#     url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
#     querystring = {"region": "CA", "symbols": sym_list}
#
#     headers = {
#         'x-rapidapi-key': settings.X_RAPIDAPI_KEY,
#         'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
#     }
#
#     response = requests.request("GET", url, headers=headers, params=querystring)
#
#     if response.status_code == 200:
#         # Deserialize the response to a python object
#         json_data = json.loads(response.text)
#         return json_data["quoteResponse"]
#     else:
#         return None

def get_quotes(request, symbols):
    #
    # Make API calls to retreive quotes for securities of interest
    #
    # sym_list = symbols
    #
    # # If sym_list is empty, return None
    # if len(sym_list) == 0:
    #     return None

    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
    querystring = {"region": "CA", "symbols": symbols}

    headers = {
        'x-rapidapi-key': settings.X_RAPIDAPI_KEY,
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    if response.status_code == 200:
        # Deserialize the response to a python object
        json_data = json.loads(response.text)
        return json_data["quoteResponse"]
    else:
        return None


# def enrich(request, list):
#     # Given a list of items (holdings, watchlist, etc), combine the list with quotes retreived
#     # from RapidAPI
#     #
#
#     symbols = []
#     # for index, value in enumerate(list):
#     #     # quote_list.append(TSXStock.objects.filter(id=value["symbol_id"]).values_list("symbol", flat=True))
#     #     symbols.append(TSXStock.objects.get(id=value["symbol_id"]).symbol)
#
#     for item in list:
#         # quote_list.append(TSXStock.objects.filter(id=value["symbol_id"]).values_list("symbol", flat=True))
#         symbols.append(TSXStock.objects.get(id=item["symbol_id"]).symbol)
#
#     sym_list = ','.join(symbols)
#
#     quotes = utils.get_quotes(request, sym_list)
#
#     combined_list = []
#     for index, value in enumerate(list):
#         x = list[index].copy()
#         x.update(quotes['result'][index])
#         combined_list.append(x)
#
#     return combined_list


def enrich(request, list):
    # Given a list of items (holdings, watchlist, etc), combine the list with quotes retreived
    # from RapidAPI
    #
    combined_list = []

    for item in list:
        symbol = TSXStock.objects.get(id=item['symbol_id']).symbol
        quote = utils.get_quotes(request, symbol)

        c = item.copy()
        try:
            c.update(quote['result'][0])
        except IndexError:
            # Quote could not be retreived for this symbol. The price change since the symbol was added
            # to the Watchlist will not be displayed
            pass

        combined_list.append(c)

    return combined_list


# def single_quote(request, symbol):
#     # Get quote for a single symbol and return the result
#     #
#
#     # s1 = []
#     # s1.append(symbol)
#     s1 = [symbol]
#     quote = utils.get_quotes(request, s1)
#     return quote


def get_txn_count(user, interval):
    # Get the number of Buy and Sell transactions for the user during the time interval
    # Note: Filtering the DateTimeField with dates will not include items on the last date
    #
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=interval)
    end_date = today + datetime.timedelta(days=1)
    txn_count = Transaction.objects.filter(user=user,
                                           txn_date__range=(start_date, end_date)) \
        .exclude(activity="D").count()
    return txn_count
