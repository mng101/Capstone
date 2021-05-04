from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone

from django.views.generic.base import TemplateView
from django.contrib import messages
from django.views.generic import (View, TemplateView, ListView, DetailView,
                                  CreateView, DeleteView, UpdateView, )
import requests
import json

from . import forms
# from .models import Account

# Create your views here.

# Define the interval during which repeated API calls for market data are to be avoided
#
MARKET_DATA_REFRESH_INTERVAL = 3600

class HomePageView(TemplateView):
    template_name = "challenge/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages.info(self.request, "hello http://example.com")
        return context


class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy("home")
    template_name = "challenge/signup.html"


class TestPageView(TemplateView):
    template_name = 'challenge/test.html'


class ThanksPageView(TemplateView):
    template_name = 'challenge/thanks.html'


def get_market_summary(request):
    #
    # Get Market Indices for Canada
    #
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-summary"

    querystring = {"region": "CA"}

    headers = {
        'x-rapidapi-key': "438c096415mshb0589791ceeff23p107e84jsnd9ed933221e3",
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    if (response.status_code == 200):
        # Deserialize the response to a python object
        json_data = json.loads(response.text)
        return json_data
    else:
        return None


def refresh_market_summary(request):
    #
    # The Market Summary is saved in the User session to avoid repeated API calls.
    # The Summary is refreshed at intervals defined by the value of MARKET_DATA_REFRESH_INTERVAL
    #
    # The timestamp for the last API call is also saved in the User session, and is used to determine
    # when the Market data is to be refreshed
    #

    # If this is a new User sesssion, create entry for "indices" and initialize the timestamp
    if "indices" not in request.session:
        request.session["indices"] = []
        request.session["indices"].append({"timestamp": 0})

    now = timezone.now().timestamp()

    # If we are past the refresh interval, refresh the data and update the timestamp
    if (now - request.session["indices"][0]["timestamp"]) > MARKET_DATA_REFRESH_INTERVAL:
        request.session['indices'].append(get_market_summary(request)['marketSummaryAndSparkResponse'])
        request.session["indices"][0]["timestamp"] = now

    return request.session['indices'][1]["result"]


    #
    # if "api_call_timestamp" not in request.session:
    #     request.session["api_call_timestamp"] = 0
    #
    # now = timezone.now().timestamp()
    #
    # if (now - request.session['api_call_timestamp']) > MARKET_DATA_REFRESH_INTERVAL:
    #     # Exceeded the refresh interval. Refresh data
    #     request.session['indices'] = get_market_summary(request)['marketSummaryAndSparkResponse']
    #
    #     # json_data is returned as an array of 15 elements. We will return the complete array for addition
    #     # into the "context". The elements to be display will be determined in the template
    #
    # return 0


class MarketsPageView(TemplateView):
    template_name = 'challenge/markets.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add list of market indices and values
        context["index_list"] = refresh_market_summary(self.request)

        # Create "indices" and "headlines" keys in the User session
        # The values retreived from the Finance API will be cached in the User session for
        # subsequent visits to the same page to limit the number of API calls during a User session.
        # The timestamp for the last API call is also saved, which is used to determine
        # when the data should be refreshed from the source

        # if "indices" not in self.request.session:
        #     self.request.session["indices"] = []
        # if "headlines" not in self.request.session:
        #     self.request.session["headlines"] = []
        # if "api_call_timestamp" not in self.request.session:
        #     self.request.session["api_call_timestamp"] = 0

        # Refresh Market Data
        # refresh_market_data(self.request)

        messages.info(self.request, "hello http://example.com")
        return context

# TODO - Compete the AccountUpdateView
#
# class AccountUpdateView(UpdateView):
#     model = Account
