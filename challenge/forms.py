from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django import forms

from .models import Account, Transaction, Watchlist, WatchlistItem


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

        def clean_first_name(self):
            cleaned_data = self.cleaned_data.get('first_name')
            # Explicit account.save() is no required
            # account.save()
            return cleaned_data


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['stock_symbol', 'activity', 'quantity']

        labels = {
            "stock_symbol": "Symbol:",
            "activity": "Action:",
            "quantity": "Quantity:",
        }


class WatchlistItemForm(ModelForm):
    class Meta:
        model = WatchlistItem
        fields = ['symbol', ]
        labels = {
            "symbol": "",
        }

    def clean_symbol(self):
        cleaned_data = self.cleaned_data.get('symbol')
        try:
            w1 = WatchlistItem.objects.get(user=self.initial['user_id'],
                                           number__number=self.initial['number_id'],
                                           symbol=cleaned_data.pk)
        except WatchlistItem.DoesNotExist:
            w1 = None
            print("Object does not exist")
            pass

        if w1 is not None:
            raise forms.ValidationError("Duplicate Symbol in Watchlist")
        # else:
        return cleaned_data

    def clean(self):
        # Check less than 10 items in the watchlist
        cleaned_data = super().clean()
        c = WatchlistItem.objects.filter(user=self.initial['user_id'],
                                         number__number=self.initial['number_id'], ).count()
        if c >= 10:
            raise forms.ValidationError("Maximum of 10 Watchlist items reached. Try another Watchlist")

        return cleaned_data
