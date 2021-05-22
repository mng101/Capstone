from django.db.models import Count, Case, When, BooleanField, Value
from challenge.models import Holding, Transaction, Watchlist

from django.utils import timezone
from django.conf import settings
import requests
import json

MARKET_DATA_REFRESH_INTERVAL = 7200

def get_quotes(request, symbols):
    #
    # Make API calls to retreive quotes for securities of interest
    #

    sym_list = symbols

    if "raw_quotes" not in request.session:
        request.session["raw_quotes"] = []

    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"

    querystring = {"region": "CA", "symbols": sym_list}

    headers = {
        'x-rapidapi-key': settings.X_RAPIDAPI_KEY,
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    if response.status_code == 200:
        # Deserialize the response to a python object
        json_data = json.loads(response.text)
        request.session["raw_quotes"].append(json_data)
    else:
        request.session["raw_quotes"] = None

    return request.session["raw_quotes"][0]["quoteResponse"]


def refresh_quotes(request, symlist):
    #
    # Quotes are saved in the User session to avoid repeated API calls. The quotes are
    # refreshed at intervals defined by the value of MARKET_DATA_REFRESH_INTERVAL. This is especially
    # useful during the development phase of the assignment.
    #
    # The timestamp for the last API call is also saved in the User session, and is used to determine
    # when the Portfolio quotes are to be retreived from the external source. A new entry for
    # portfolio_quotes is created, if one does not exist
    #
    if "portfolio_quotes" not in request.session:
        request.session["portfolio_quotes"] = []
        request.session["portfolio_quotes"].append({'timestamp': 0})

    now = timezone.now().timestamp()

    # Get new data if we are past the refresh interval
    if (now - request.session["portfolio_quotes"][0]["timestamp"]) > MARKET_DATA_REFRESH_INTERVAL:
        request.session["portfolio_quotes"].append(get_quotes(request, symlist))
        request.session["portfolio_quotes"][0]["timestamp"] = now

    return request.session["portfolio_quotes"][1]

def enrich(request, portfolio_list):
    p = portfolio_list
    return p
