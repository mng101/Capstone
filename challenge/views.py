from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
# from django.template import Library
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

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
from .models import Account, Holding, Transaction, Watchlist
from .forms import AccountForm, TransactionForm
from . import utils
from decimal import Decimal

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


class MarketsPageView(TemplateView):
    template_name = 'challenge/markets.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add market indices and values
        # context["index_list"] = refresh_market_summary(self.request)
        context["index_list"] = utils.get_market_summary(self.request)
        # Add News Headlines to the context
        context["news_headlines"] = utils.get_news_headlines(self.request)
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

        # Get quotes for all the symbols in the portfolio.
        p_quotes = utils.get_quotes(self.request, sym_list)

        if (p_quotes is not None):

            # Get a list of holdings and convert to a list of dictionaries
            h_list = Holding.objects.filter(user=self.request.user).values()

            # Combine holdings and quotes into a consolidated list
            c_list = []
            for index, value in enumerate(h_list):
                x = h_list[index].copy()
                x.update(p_quotes['result'][index])
                c_list.append(x)

            # Add some calculated values to the combined list
            for item in c_list:
                item.update(
                    {'avg_price': (item['total_cost'] / item['no_of_shares_owned']),
                     # 'volume': (item['regularMarketVolume'] / 1000),
                     'volume': '{:,}'.format(math.trunc(item['regularMarketVolume'] / 1000)),
                     'market_value': (item['bid'] * item['no_of_shares_owned']),
                     'change': (Decimal(item['bid'] * item['no_of_shares_owned']) - item['total_cost']),
                     }
                )
            return c_list
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add Account details to the context
        context["account"] = Account.objects.get(user=self.request.user)
        # Compute total value of investments
        investments = 0
        if (context['object_list'] is not None):
            for h in context['object_list']:
                investments += (h['no_of_shares_owned'] * h['bid'])
        context["investments"] = investments
        context["portfolio_total"] = (context["account"].cash + Decimal(investments))
        return context


class WatchlistView(ListView):
    model = Watchlist
    template_name = 'challenge/watchlist.html'


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm

    login_url = 'login'

    def form_valid(self, form):
        form.instance.user_id = self.request.user
        form.instance.valid = False
        return super(TransactionCreateView, self).form_valid(form)
