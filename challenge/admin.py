from django.contrib import admin

# Register your models here.

from challenge.models import User, Account, TSXStock, Holding, Watchlist, WatchlistItem, Transaction

admin.site.register(User)
admin.site.register(Account)
admin.site.register(TSXStock)
admin.site.register(Holding)
admin.site.register(Watchlist)
admin.site.register(WatchlistItem)
admin.site.register(Transaction)
