import datetime
import json
import math
from decimal import Decimal

from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import (TemplateView, ListView, CreateView, UpdateView, )

from . import forms
from . import utils
from .forms import AccountForm, TransactionForm, WatchlistItemForm
from .models import Account, TSXStock, Holding, Watchlist, WatchlistItem, Transaction


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


class ThanksPageView(TemplateView):
    template_name = 'challenge/logout.html'


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
        # Get the list of Portfolio Holdings and append with quotes from RapidAPI
        #
        holdings = Holding.objects.filter(user=self.request.user).values()

        combined_list = utils.enrich(self.request, holdings)

        # Add some calculated values to the combined list
        for item in combined_list:
            try:
                item.update(
                    {'avg_price': (item['total_cost'] / item['no_of_shares_owned']),
                     'volume': '{:,}'.format(math.trunc(item['regularMarketVolume'] / 1000)),
                     'market_value': (item['bid'] * item['no_of_shares_owned']),
                     'change': (Decimal(item['bid'] * item['no_of_shares_owned']) - item['total_cost']),
                     }
                )
            except KeyError:
                # KeyError is a result of missing Quote data. The object will not contain the 'Symbol'
                # Update the object with the Symbol retreived from TSXStock
                symbol = TSXStock.objects.get(id=item['symbol_id']).symbol
                item.update(
                    {'symbol': symbol, }
                )
                messages.info(self.request, ("Market Data not available for ", symbol))

        return combined_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add Account details to the context
        context["account"] = Account.objects.get(user=self.request.user)
        # Compute total value of investments
        investments = 0
        if context['object_list'] is not None:
            for h in context['object_list']:
                investments += (h['no_of_shares_owned'] * h['bid'])
        context["investments"] = investments
        context["portfolio_total"] = (context["account"].cash + Decimal(investments))
        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class WatchlistView(LoginRequiredMixin, CreateView):
    model = Watchlist
    form_class = WatchlistItemForm
    template_name = 'challenge/watchlist.html'

    login_url = 'login'

    def get_initial(self):
        print("Get Initial")
        return {'number_id': self.kwargs['pk'],
                'user_id': self.request.user.id, }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["watchlist"] = Watchlist.objects.get(user=self.request.user, number=self.kwargs['pk'])
        context['watchlistitem_form'] = WatchlistItemForm()

        # Get the items in the Watchlist formatted as a list of dictionaries
        # watchlist_items = WatchlistItem.objects.filter(user=self.request.user,
        #                                                number__number=self.kwargs['pk']).values()
        watchlist_items = WatchlistItem.objects.filter(user=self.request.user,
                                                       number=self.kwargs['pk']).values()
        # Merge Watchlist Items with RapidAPI Quotes
        combined_list = utils.enrich(self.request, watchlist_items)

        # Add the price_change for each of the items
        for item in combined_list:
            try:
                item.update(
                    {'price_change': (Decimal(item['ask']) - item['price_when_added']), }
                )
            except KeyError:
                # KeyError is a result of missing Quote data. The object will not contain the 'Symbol'
                # Update the object with the Symbol retreived from TSXStock
                symbol = TSXStock.objects.get(id=item['symbol_id']).symbol
                item.update(
                    {'symbol': symbol, }
                )
                messages.info(self.request, ("Market Data not available for ", symbol))
        context['watchlist_items'] = combined_list
        return context

    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        form.instance.number = self.kwargs['pk']
        symbol_quote = utils.single_quote(self.request, form.instance.symbol.symbol)

        if len(symbol_quote['result']) > 0:
            form.instance.price_when_added = ((Decimal(symbol_quote['result'][0]['bid']) +
                                               Decimal(symbol_quote['result'][0]['ask'])) / 2)
            form.instance.date_added = datetime.date.today()
            form.instance.valid = True
        else:
            form.instance.valid = False
            raise forms.ValidationError("Quote data not available for this symbol. Try Another")

        return super().form_valid(form)

    def form_invalid(self, form):
        print("In form_invalid")
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


@login_required()
def updatetitle(request, pk):
    if request.method != "PUT":
        return JsonResponse({"error": "Post request required."}, status=400)
    print("Executing _updatetitle in views.py")

    data = json.loads(request.body)

    w1 = Watchlist.objects.get(id=pk)
    w1.title = data["title"]
    w1.save()

    return JsonResponse({"message": "Update successful"}, status=200)


# TODO - WatchlistItemDeleteView

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    success_url = reverse_lazy("dashboard")

    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cash"] = Account.objects.get(user=self.request.user).cash
        #
        # Get the number of trades in the last 2 weeks (14 days)
        # Note: Filtering the DateTimeField with dates will not include items on the last date
        #
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=14)
        end_date = today + datetime.timedelta(days=1)
        context["txn_count"] = Transaction.objects.filter(user=self.request.user,
                                                          txn_date__range=(start_date, end_date)).count()

        context["holding_count"] = Holding.objects.filter(user=self.request.user).count()

        return context

    def form_valid(self, form):
        # form.instance.user_id = self.request.user
        self.object = form.save(commit=False)
        form.instance.user = self.request.user
        form.instance.valid = False
        return super(TransactionCreateView, self).form_invalid(form)

    def form_invalid(self, form):
        print("In form_invalid")
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    login_url = 'login'
    context_object_name = "txn_history"

    def get_queryset(self):
        # Get the list of transactions for the User
        s1 = Transaction.objects.filter(user=self.request.user).annotate(value=F('price') * F('quantity'))
        return s1
