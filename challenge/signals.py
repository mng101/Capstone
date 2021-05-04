# from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Account

'''
    TODO - The following code works perfectly when included in models.py
           and fails when copied to this signals.py file
           Will work with models.py file for now, and come back if time permits
'''

# # @receiver(post_save, sender=User)
# def create_user_account(sender, instance, created, **kwargs):
#     if created:
#         Account.objects.create(user=instance)
#         print('Account created')
#
# post_save.connect(create_user_account, sender=User)
