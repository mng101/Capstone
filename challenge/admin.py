from django.contrib import admin

# Register your models here.

from challenge.models import User, Account, Holding, Transaction

admin.site.register(User)
admin.site.register(Account)
admin.site.register(Holding)
admin.site.register(Transaction)
