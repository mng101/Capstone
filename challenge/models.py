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


# TODO - Strictly speaking, the Holding model should not be required. It is possible to derive the list of
#        holdings from the transactions. This will mean more coding and slower processing. Will leave this
#        decision ot a later date.
#        For a start, both the Transaction, and Holding models will be updated with relevant values for each
#        Trade excuted

class Holding(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='holdings')
    stock_symbol = models.CharField(max_length=6, null=False)
    company_name = models.CharField(max_length=64)
    no_of_shares_owned = models.IntegerField(default=0)
    # no_of_shared_owned is totaled from all the trades for this security
    total_cost = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    # total_cost is the sum total of the cost of all related transactions

    def __str__(self):
        return f"{self.stock_symbol} - {self.company_name} - {self.no_of_shares_owned} - {self.total_cost}"


# The Transaction model will hold the trades executed by the User. Trades will be settled immediately at the mid
# point between the 'bid' and 'ask' values for the security being traded. The Holding model must be updated at the
# same time as the Transaction model. In addition, the 'cash' balance in the Account model must be updated. Using
# signals is probably the easiest approach to synchronizing the updates

class Transaction (models.Model):
    ACTIVITIES = (
        ('B', 'Buy'),
        ('S', 'Sell'),
        ('D', 'Dividend'),
    )
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="transactions")
    stock_symbol = models.CharField(max_length=6, null=False)
    activity = models.CharField(max_length=1, choices=ACTIVITIES)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    txn_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_symbol} {self.activity} - {self.quantity} {self.price} - {self.txn_date}"


class Watchlist(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="watchlists")
    num = models.IntegerField(null=False)
    title = models.CharField(max_length=64)
    stock_symbol = models.CharField(max_length=6, null=False)
    date_listed = models.DateField(auto_now_add=True)
    price_when_listed = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)


'''
TODO - Move the 'create_user_account' function to signals.py file, if time permits.
       The code failed during initial testing in signals.py file
'''

'''
    When a user registers at the site, an Account is automatically created to track contact details, and the
    cash balance. The $250,000 grated to the user on registration is defined in the Account model.
    A set of 5 watchlist are also created, which the user can populate with stocks they wish to track.
'''
@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
        print('Account created')


'''
    Every trade submitted, requires 2 additional updates.
    1. Create a new Holding object, or update if one for the same security exists
    2. Update the cash balance in the Account object
    These 2 updates are managed by the post_save signal from the Transaction model
'''
@receiver(post_save, sender=Transaction)
def create_update_holding(sender, instance, created, **kwargs):
    print('Holding model received signal')

    if created:
        try:
            # Create or Update Holding
            holding = Holding.objects.get(stock_symbol=instance.stock_symbol)
            if (instance.activity == "B"):
                # Adding to existing holding
                holding.no_of_shares_owned += instance.quantity
                holding.total_cost += (instance.quantity * instance.price)
            else:
                # If not buying, selling is assumed, for manually entered trades.
                # Reducing existing holding. Quantity sold is less than or equal to the no_of_shares_owned is
                # previously confirmed during trade entry
                holding.no_of_shares_owned -= instance.quantity
                # If the no_of_shares_owned are all sold, the total_cost is not relevant. A positive total_cost
                # implies a trade profit, else the trade loss
                holding.total_cost -= (instance.quantity * instance.price)

            holding.save()

        except Holding.DoesNotExist:
            # Create a new Holding object
            Holding.objects.create(user=instance.user, stock_symbol=instance.stock_symbol,
                                   no_of_shares_owned=instance.quantity,
                                   total_cost = (instance.quantity * instance.price))
        print('Holding Update')

        # Update cash balance in Account
        account = Account.objects.get(user=instance.user)
        if (instance.activity == 'B'):
            account.cash -= (instance.quantity * instance.price)
        else:
            account.cash += (instance.quantity * instance.price)
        account.save()
        print('Account Update')
