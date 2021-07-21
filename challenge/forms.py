from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.http import HttpResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django import forms

from .models import Account, Transaction, Watchlist, WatchlistItem, Holding


class UserCreateForm(UserCreationForm):
    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Login name"
        self.fields["email"].label = "Email address"


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'middle_name', 'last_name', 'address1', 'address2', 'city',
                  'province', 'postal_code']

        labels = {
            "user": "Your Login",
            "first_name": "First Name",
            "middle_name": "Middle Name",
            "last_name": "Last Name",
        }
        # widgets = {
        #     'user': setattr(
        # }

        # def clean_first_name(self):
        #     cleaned_data = self.cleaned_data.get('first_name')
        #     # Explicit account.save() is not required
        #     # account.save()
        #     return cleaned_data


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['symbol', 'activity', 'quantity', 'price', 'amount', ]
        # When the form is first displayed only the symbol and activity fields are displayed.
        # The other fields are hidden using CSS properties "display:none"
        # The appropriate fields are displayed by the Javascript function, based on the input
        # to the 'activity' field

        labels = {
            "symbol": "Symbol:",
            "activity": "Action:",
            "quantity": "Quantity:",
            "price": "Price",
            "amount": "Amount",
        }

        widgets = {
            'activity': forms.Select(attrs = {'onchange': 'recordActivity(this.value)'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TransactionForm, self).__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')

        if (self.cleaned_data.get('activity') in ('B', 'S')) \
            and (quantity < 1):
            raise forms.ValidationError("Quantity must be more than 0 for Buy and Sell orders")
        return quantity

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if (amount <= 0):
            raise forms.ValidationError("Transaction amount must be more than 0, for all transactions")
        return amount

    def clean(self):
        sym = self.cleaned_data.get('symbol')
        activity = self.cleaned_data.get('activity')

        # Verify symbol in Holding list for dividend transactions
        if (activity == "D"):
            try:
                Holding.objects.get(user=self.user, symbol=sym)
                # If object exists, continue
                pass
            except ObjectDoesNotExist:
                raise forms.ValidationError("This symbol is not in the Holding list. You cannot receive dividends")

        return self.cleaned_data

        # Verify cash exists for Buy transactions




    # def clean(self):
    #     # Check Transaction Validity
    #     # 1. Cash exists to cover a Buy transaction
    #     # 2. Sell transactions are only permitted for Symbols and Quantity in the portfolio
    #     # 3. Dividends are only permitted for Symbols in the portfolio
    #     # 4. Maximum of 10 trades (Buy/Sell) permitted in a 10 day interval
    #     # 5. Exception to the 10 trades in less than 5 holdings
    #     #
    #     print ("In form clean")
    #     cleaned_data = super().clean()
    #
    #     cash = Account.objects.get(user=self.request.user).cash
    #
    #
    #     # if c >= 10:
    #     #     raise forms.ValidationError("Maximum of 10 Watchlist items reached. Try another Watchlist")
    #
    #     return cleaned_data


class WatchlistItemForm(ModelForm):
    class Meta:
        model = WatchlistItem
        fields = ['symbol', ]
        labels = {
            "symbol": "",
        }

    def clean_symbol(self):
        symbol = self.cleaned_data.get('symbol')
        try:
            # w1 = WatchlistItem.objects.get(user=self.initial['user_id'],
            #                                number__number=self.initial['number_id'],
            #                                symbol=cleaned_data.pk)
            w1 = WatchlistItem.objects.get(user=self.initial['user_id'],
                                           number=self.initial['number_id'],
                                           symbol=cleaned_data.pk)
        except WatchlistItem.DoesNotExist:
            w1 = None
            print("Object does not exist")
            pass

        if w1 is not None:
            raise forms.ValidationError("Duplicate Symbol in Watchlist")
        # else:
        return symbol

    def clean(self):
        # Check less than 10 items in the watchlist
        cleaned_data = super().clean()
        # c = WatchlistItem.objects.filter(user=self.initial['user_id'],
        #                                  number__number=self.initial['number_id'], ).count()
        c = WatchlistItem.objects.filter(user=self.initial['user_id'],
                                         number=self.initial['number_id'], ).count()
        if c >= 10:
            raise forms.ValidationError("Maximum of 10 Watchlist items reached. Try another Watchlist")

        return cleaned_data
