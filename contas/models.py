from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='wallet',
        on_delete=models.CASCADE
    )
    balance = models.DecimalField(
        _('Balance'),
        decimal_places=2,
        max_digits=10,
        default=Decimal('1000.00')
    )

    def __str__(self):
        return '%s - %s' % (self.user.username, self.balance)
