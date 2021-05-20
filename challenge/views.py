from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
# from django.template import Library

# Import django settings to access the Rapid API Key
from django.conf import settings

from django.views.generic.base import TemplateView
from django.contrib import messages
from django.views.generic import (View, TemplateView, ListView, DetailView,
                                  CreateView, DeleteView, UpdateView, )
import requests
import json
import numpy
import math

from . import forms
from .models import Account, Holding, Watchlist
from .forms import AccountForm
from . import utils
from decimal import Decimal

# Define the interval during which repeated API calls for market data are to be avoided
#
MARKET_DATA_REFRESH_INTERVAL = 15


# register = Library()

# Create your views here.


class HomePageView(TemplateView):
    template_name = "challenge/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # messages.info(self.request, "hello http://example.com")
        return context


class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy("home")
    template_name = "challenge/signup.html"


class TestPageView(TemplateView):
    template_name = 'challenge/test.html'


class ThanksPageView(TemplateView):
    template_name = 'challenge/thanks.html'


# def get_market_summary(request):
#     #
#     # Get Market Summary for Canada - Original logic
#     # The original code make an API call everytime the function is called.
#     # Use the updated logic below during development to minimize external calls.
#     #
#     url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-summary"
#
#     querystring = {"region": "CA"}
#     headers = {
#         'x-rapidapi-key': settings.X_RAPIDAPI_KEY,
#         'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
#     }
#
#     response = requests.request("GET", url, headers=headers, params=querystring)
#     if response.status_code == 200:
#         # Deserialize the response to a python object
#         json_data = json.loads(response.text)
#         return json_data['marketSummaryAndSparkResponse']
#     else:
#         return None


def get_market_summary(request):
    #
    # Get Market Summary for Canada - Updated logic
    # This is temporary logic to save the json response in the User session, and always return the
    # cached data. This code is suitable for debugging the views without generating excessive number
    # of API calls. The original logic above (commented out) should be used to activate live data
    #

    # TODO - Revert back to the original logic after testing

    if "market_summary" not in request.session:
        request.session["market_summary"] = []

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
            request.session["market_summary"].append(json_data)
        else:
            request.session["market_summary"] = None

    # Original code commented out
    # TODO - Cleanup here
    return request.session["market_summary"][0]["marketSummaryAndSparkResponse"]

    # return request.session["market_summary"][0]


# def get_news_headlines(request):
#     #
#     # Get the News Headlines for Canada
#     #
#     url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/list"
#
#     querystring = {"region": "CA", "snippetCount": "10"}
#
#     payload = "Pass in the value of uuids field returned right in this endpoint to load the next" \
#               " page, or leave empty to load first page "
#     headers = {
#         'content-type': "text/plain",
#         'x-rapidapi-key': "438c096415mshb0589791ceeff23p107e84jsnd9ed933221e3",
#         'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
#     }
#
#     response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
#     if response.status_code == 200:
#         # Deserialize the response to a python object
#         json_data = json.loads(response.text)
#         return json_data
#     else:
#         return None


# def split_into_columns(indices, n):
#     # Split the list into n columns to display as a table
#     # Adapted from //djangosnippets.org/snippets/401
#     try:
#         items = list(indices)
#         columns = int(n)
#     except (ValueError, TypeError):
#         return [indices]
#
#     list_len = len(items)
#     rows = list_len // columns
#
#     if list_len % n != 0:
#         rows += 1
#
#     return [items[split * i:split * (i + 1):split * (i + 2)] for i in range(n)]

def get_news_headlines(request):
    #
    # Get the News Headlines for Canada - Updated Logic
    #

    # TODO - Revert back to the original logic after testing

    if "market_news" not in request.session:
        request.session["market_news"] = []

        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/list"
        querystring = {"region": "CA", "snippetCount": "10"}
        payload = "Pass in the value of uuids field returned right in this endpoint to load the next page, or leave " \
                  "empty to load first page "
        headers = {
            'content-type': "text/plain",
            # 'x-rapidapi-key': "438c096415mshb0589791ceeff23p107e84jsnd9ed933221e3",
            'x-rapidapi-key': settings.X_RAPIDAPI_KEY,
            'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        if response.status_code == 200:
            # Deserialize the response to a python object
            json_data = json.loads(response.text)
            request.session["market_news"].append(json_data)
        else:
            request.session["market_news"] = None

        return request.session["market_news"][0]


def refresh_market_summary(request):
    #
    # The Market Summary is saved in the User session to avoid repeated API calls.
    # The Summary is refreshed at intervals defined by the value of MARKET_DATA_REFRESH_INTERVAL
    # The MarketsPageView calls refresh_market_summary which in turn calls get_market_summary
    #
    # The timestamp for the last API call is also saved in the User session, and is used to determine
    # when the Market data is to be refreshed

    # If this is a new User sesssion, create entry for "indices" and initialize the timestamp
    if "indices" not in request.session:
        request.session["indices"] = []
        request.session["indices"].append({"timestamp": 0})

    now = timezone.now().timestamp()

    # If we are past the refresh interval, get updated data and update the timestamp
    if (now - request.session["indices"][0]["timestamp"]) > MARKET_DATA_REFRESH_INTERVAL:
        # Delete stale data previously saved in the session
        try:
            request.session["indices"].pop(1)
            print("deleting stale data, if it exists")
        except IndexError:
            pass  # "indices" newly created. No stale data to delete

        # Append refreshed market data
        print("Refreshing Market Indices")
        request.session['indices'].append(get_market_summary(request))
        request.session["indices"][0]["timestamp"] = now

    # Split the array returned into 3 colums and 5 rows
    # return numpy.array_split(request.session['indices'][1]["marketSummaryAndSparkResponse"]["result"], 5)
    # Splitting the results into 3 columns is no longer required
    #
    # Original code copied below
    # TODO - Cleanup here
    # return numpy.array_split(request.session['indices'][1]["result"], 5)
    return request.session['indices'][1]["result"]


def refresh_news_headlines(request):
    if "news_headlines" not in request.session:
        request.session["news_headlines"] = []
        request.session["news_headlines"].append({"timestamp": 0})

    now = timezone.now().timestamp()

    # If we are past the refresh interval, refresh the data and update the timestamp
    if (now - request.session["news_headlines"][0]["timestamp"]) > MARKET_DATA_REFRESH_INTERVAL:
        request.session['news_headlines'].append(get_news_headlines(request))
        request.session["news_headlines"][0]["timestamp"] = now

    return request.session["news_headlines"][1]["data"]["main"]["stream"]


class MarketsPageView(TemplateView):
    template_name = 'challenge/markets.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add market indices and values
        context["index_list"] = refresh_market_summary(self.request)

        # Add News Headlines to the context
        context["news_headlines"] = refresh_news_headlines(self.request)

        return context


class AccountUpdateView(UpdateView):
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy("home")


class HoldingListView(ListView):
    model = Holding
    template_name = 'challenge/dashboard.html'

    def get_queryset(self):
        # Get the list of symbols in the portfolio and format the list suitable for RapidAPI
        s1 = Holding.objects.filter(user=self.request.user).values_list('stock_symbol', flat=True)
        sym_list = ','.join(s1)

        # Get quotes for all the symbols in the portfolio. "refresh_quotes" will return values in
        # session cache if the previous request was less than 1 hour ago
        p_quotes = utils.refresh_quotes(self.request, sym_list)

        # Get a list of holdings and convert to a list of dictionaries
        h_list = Holding.objects.filter(user=self.request.user).values()

        # Combine holdings and quotes into a consolidated list
        c_list = []
        for index, value in enumerate(h_list):
            x = h_list[index].copy()
            # x.update(self.request.session['portfolio_quotes'][1]['result'][index])
            x.update(p_quotes['result'][index])
            c_list.append(x)

            # Add some calculated values to the combined list
            for item in c_list:
                item.update (
                    {'avg_price': (item['total_cost'] / item['no_of_shares_owned']),
                     # 'volume': (item['regularMarketVolume'] / 1000),
                     'volume': '{:,}'.format(math.trunc(item['regularMarketVolume'] / 1000)),
                     'market_value': (item['bid'] * item['no_of_shares_owned']),
                     'change': (Decimal(item['bid'] * item['no_of_shares_owned']) - item['total_cost']),
                     }
                )
            # for item in c_list:
            #     item

        return c_list

        # list = [{'stock_symbol': x.stock_symbol, 'company_name': x.company_name,
        #         'no_of_shares_owned': x.no_of_shares_owned, 'avg_price': (x.total_cost / x.no_of_shares_owned),
        #         'total_cost': x.total_cost}
        #        for x in Holding.objects.filter(user=self.request.user)]
        # return list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add Account details to the context
        context["account"] = Account.objects.get(user=self.request.user)

        # Compute total value of investments
        investments = 0
        for h in context['object_list']:
            investments += (h['no_of_shares_owned'] * h['bid'])
        context["investments"] = investments
        context["portfolio_total"] = (context["account"].cash + Decimal(investments))

        return context


class WatchlistView(ListView):
    model = Watchlist
    template_name = 'challenge/watchlist.html'
