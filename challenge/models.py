from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class User(AbstractUser):
    pass


class Account(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE,
                                primary_key=True, related_name="accounts")
    first_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    address1 = models.CharField(max_length=64, null=True)
    address2 = models.CharField(max_length=64, null=True)
    city = models.CharField(max_length=32, null=True)
    province = models.CharField(max_length=32, null=True)
    postal_code = models.CharField(max_length=16, null=True)
    member_since = models.DateField(auto_now_add=True)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=250000)

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name} - {self.cash} - {self.member_since}"

# TODO - Move the 'create_user_account' function to signals.py file, if time permits.
#        The code failed during initial testing in signals.py file

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
        print('Account created')


#
# TODO - Strictly speaking, the Holding model should not be required. It is possible to derive the list of
#        holdings from the transactions. This will mean more coding and slower processing. Will leave this
#        decision ot a later date.
#        For a start, both the Transaction, and Holding models will be updated with relevant values for each
#        Trade excuted
#

class Holding(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='holdings')
    stock_symbol = models.CharField(max_length=6, null=False)
    company_name = models.CharField(max_length=64)
    no_of_shares_owned = models.IntegerField(default=0)
    # no_of_shared_owned is totaled from all the trades for this security
    total_cost = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    # total_cost is the sum total of the cost of all related transactions

    def __str__(self):
        return f"{self.stock_symbol} - {self.company_name} - {self.no_of_shares_owned} - {self.average_cost}"

# @receiver(post_save, sender=Transaction)
# def create_update_holding(sender, instance, created, **kwargs):
#     if created:
#         print('Holding model received signal')
#         print('Account created')
#
#
# #
# #   The Transaction model will hold the trades executed by the User. Trades will be settled immediately at the mid
# #   point between the 'bid' and 'ask' values for the security being traded. The Holding model must be updated at the
# #   same time as the Transaction model. In addition, the 'cash' balance in the Account model must be updated. Using
# #   signals is probably the easiest approach to synchronizing the updates
# #
#
# class Transaction (models.Model):
#     ACTIVITIES = (
#         ('B', 'Buy'),
#         ('S', 'Sell'),
#         ('D', 'Dividend'),
#     )
#     user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="transactions")
#     stock_symbol = models.CharField(max_length=6, null=False)
#     activity = models.CharField(max_length=1, choices=ACTIVITIES)
#     quantity = models.IntegerField(default=0)
#     price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
#     txn_date = models.DateField(auto_now_add=True)
