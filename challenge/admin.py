from django.contrib import admin

# Register your models here.

from challenge.models import User, Account

admin.site.register(User)
admin.site.register(Account)
