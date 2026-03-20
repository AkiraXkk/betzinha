from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import json

from apostas.models import Bet
from contas.models import Wallet
from partidas.models import Match
from times.models import Team, League


class BetCreateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jogador', password='123456')
        self.league = League.objects.create(name='Série A', country='Brasil')
        self.home = Team.objects.create(name='Time Casa')
        self.away = Team.objects.create(name='Time Fora')
        self.match = Match.objects.create(
            home_team=self.home,
            visiting_team=self.away,
            date=timezone.now(),
            home_win=Decimal('2.00'),
            draw=Decimal('3.00'),
            visiting_win=Decimal('4.00'),
            league=self.league
        )
        self.url = reverse('apostas:realizar-aposta')

    def test_should_reject_negative_bet_value(self):
        self.client.login(username='jogador', password='123456')

        response = self.client.get(self.url, {
            'data': json.dumps({str(self.match.pk): 'home_win'}),
            'betsvalue': '-10'
        })

        body = json.loads(response.content.decode('utf-8'))
        self.assertFalse(body['success'])
        self.assertEqual(Bet.objects.count(), 0)

    def test_should_reject_bet_when_balance_is_insufficient(self):
        self.client.login(username='jogador', password='123456')
        Wallet.objects.create(user=self.user, balance=Decimal('10.00'))

        response = self.client.get(self.url, {
            'data': json.dumps({str(self.match.pk): 'home_win'}),
            'betsvalue': '11'
        })

        body = json.loads(response.content.decode('utf-8'))
        self.assertFalse(body['success'])
        self.assertEqual(Bet.objects.count(), 0)

    def test_should_create_bet_and_debit_wallet_when_payload_is_valid(self):
        self.client.login(username='jogador', password='123456')
        Wallet.objects.create(user=self.user, balance=Decimal('100.00'))

        response = self.client.get(self.url, {
            'data': json.dumps({str(self.match.pk): 'home_win'}),
            'betsvalue': '10'
        })

        body = json.loads(response.content.decode('utf-8'))
        self.assertTrue(body['success'])
        self.assertEqual(Bet.objects.count(), 1)
        wallet = Wallet.objects.get(user=self.user)
        self.assertEqual(wallet.balance, Decimal('90.00'))
