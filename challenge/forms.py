from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import Account, Transaction


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
            account.save()
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
