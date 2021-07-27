from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm

from . import utils
from .models import Account, Transaction, WatchlistItem, Holding


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

        if (self.cleaned_data.get('activity') in ('B', 'S')):
            if (quantity < 1):
                raise forms.ValidationError("Quantity must be more than 0 for Buy and Sell orders")
            if (quantity % 10 != 0):
                raise forms.ValidationError("Quantity must be in multiples of 10")
        return quantity

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if (amount <= 0):
            raise forms.ValidationError("Transaction amount must be more than 0, for all transactions")
        return amount

    def clean(self):
        #
        # Check transaction validity

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

        # Verify sufficient cash to cover Buy transaction
        if (activity == "B"):
            cash = Account.objects.get(user=self.user).cash
            if (self.cleaned_data.get('amount') > cash):
                raise forms.ValidationError("Insufficient funds to cover this transaction")

        # Verifiy Holding count less than 10 for Buy transactions. If equal to 10, Buy is only permitted for
        # symbols already in the Holding list
        if (Holding.objects.filter(user=self.user).count == 10):
            try:
                Holding.objects.filter(user=self.user, symbol=sym)
                # If object exists, continue
                pass
            except ObjectDoesNotExist:
                raise forms.ValidationError("This transaction will exceed the maximum number of permitted holdings")

        # For sell transactions, verify holding and number of shares
        if (activity == "S"):
            try:
                q = Holding.objects.get(user=self.user, symbol=sym)
                if (q.no_of_shares_owned < self.cleaned_data.get('quantity')):
                    raise forms.ValidationError("Sell quantity exceeds holding. Short selling not supported")
            except ObjectDoesNotExist:
                raise forms.ValidationError("Symbol not in the holdings. Short selling not supported")

        # For Buy and Sell transactions, check less than 10 transactions in the last 10 business days (14 calendar days)
        if (activity in ("B", "S")):
            txn_count = utils.get_txn_count(self.user, 14)
            if (txn_count >= 10) and (Holding.objects.filter(user=self.user).count >= 7):
                raise forms.ValidationError("Permitted transaction count exceeded. Try again another day !!")

        return self.cleaned_data


class WatchlistItemForm(ModelForm):
    class Meta:
        model = WatchlistItem
        fields = ['symbol', ]
        labels = {
            "symbol": "",
        }

    def clean_symbol(self):
        sym_to_add = self.cleaned_data.get('symbol')
        try:
            w1 = WatchlistItem.objects.get(user=self.initial['user_id'],
                                           number=self.initial['number_id'],
                                           symbol=sym_to_add)
        except WatchlistItem.DoesNotExist:
            w1 = None
            print("Object does not exist")
            pass

        if w1 is not None:
            raise forms.ValidationError("Duplicate Symbol in Watchlist")
        # else:
        return sym_to_add

    def clean(self):
        # Check less than 10 items in the watchlist
        cleaned_data = super().clean()
        c = WatchlistItem.objects.filter(user=self.initial['user_id'],
                                         number=self.initial['number_id'], ).count()
        if c >= 10:
            raise forms.ValidationError("Maximum of 10 Watchlist items reached. Try another Watchlist")

        return cleaned_data
