from django.contrib import admin

# Register your models here.

from challenge.models import User, Account, Holding

admin.site.register(User)
admin.site.register(Account)
admin.site.register(Holding)
