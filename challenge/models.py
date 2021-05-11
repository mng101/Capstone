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
    average_cost = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.stock_symbol} - {self.company_name} - {self.no_of_shares_owned} - {self.average_cost}"
