import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.views import generic
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from . import models
from contas.models import Wallet
from partidas.models import Match

VALID_BET_TYPES = ('home_win', 'draw', 'visiting_win')
MAX_STORED_BET_VALUE = Decimal('99.99')


class BetCreateView(generic.View):
    model = models.Bet

    @cached_property
    def user(self):
        is_authenticated = self.request.user.is_authenticated
        if callable(is_authenticated):
            is_authenticated = is_authenticated()
        if is_authenticated:
            return self.request.user
        return None

    @cached_property
    def value(self):
        value = self.request.GET.get('betsvalue', None)
        if value is None:
            return value
        try:
            return Decimal(value.replace(',', '.'))
        except (InvalidOperation, AttributeError):
            return None

    def json_response(self, success, message):
        return HttpResponse(
            json.dumps({'success': success, 'message': str(message)}),
            content_type='application/json'
        )

    @transaction.atomic
    def get(self, *args, **kwargs):
        if self.user is None:
            return self.json_response(False, _('You need to be logged in to place bets.'))
        if self.value is None:
            messages.info(self.request, _('Bet\'s value not defined'))
            return self.json_response(False, _('Bet\'s value not defined'))
        if self.value <= Decimal('0'):
            return self.json_response(False, _('Bet value must be greater than zero.'))
        try:
            data = json.loads(self.request.GET.get('data', '{}'))
        except ValueError:
            return self.json_response(False, _('Invalid bet payload.'))
        if not data:
            return self.json_response(False, _('No bets selected.'))
        wallet, created = Wallet.objects.select_for_update().get_or_create(user=self.user)
        if wallet.balance < self.value:
            return self.json_response(False, _('Insufficient balance for this bet.'))
        for key, bet_type in data.items():
            if bet_type not in VALID_BET_TYPES:
                return self.json_response(False, _('Invalid bet type.'))
            try:
                match = Match.objects.get(pk=key)
            except Match.DoesNotExist:
                return self.json_response(False, _('Selected match does not exist.'))
            if not self.can_store_bet_value(match, bet_type):
                return self.json_response(False, _('Bet value is too high for the current market limits.'))
            self.create_bet(match, bet_type)
        wallet.balance -= self.value
        wallet.save(update_fields=['balance'])
        return self.json_response(True, _('Bet successfully placed.'))

    def can_store_bet_value(self, match, bet_type):
        calculated_value = self.value * Decimal(str(getattr(match, bet_type)))
        return calculated_value <= MAX_STORED_BET_VALUE

    def create_bet(self, match, type):
        '''
        Cria aposta com dados passado pelo usuario na view
        '''
        self.model.objects.create_with_code(
            user=self.user, match=match,
            value=self.value * Decimal(str(getattr(match, type))),
            type=_(type)
        )
