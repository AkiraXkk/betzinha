import json
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from django.views import generic

from . import models
from times.models import League
from contas.models import Wallet


class MatchListView(generic.ListView):
    model = models.Match

    def get_context_data(self, **kwargs):
        context = super(MatchListView, self).get_context_data(**kwargs)
        now = timezone.localtime(timezone.now())
        context['object_list'] = {league: self.object_list.filter(league=league.pk)
                                  for league in League.objects.all()}
        context['now'] = now
        context['user_balance'] = None
        is_authenticated = self.request.user.is_authenticated
        if callable(is_authenticated):
            is_authenticated = is_authenticated()
        if is_authenticated:
            context['user_balance'] = Wallet.objects.filter(user=self.request.user).values_list('balance', flat=True).first()
        return context


class MatchOddsFeedView(generic.View):
    def get(self, request, *args, **kwargs):
        now = timezone.localtime(timezone.now())
        matches = models.Match.objects.all()
        payload = {}
        for match in matches:
            time_left = match.date - now
            payload[str(match.pk)] = {
                'home_win': str(match.home_win),
                'draw': str(match.draw),
                'visiting_win': str(match.visiting_win),
                'is_live': time_left <= timedelta(minutes=0),
                'seconds_to_start': max(int(time_left.total_seconds()), 0),
            }
        return HttpResponse(json.dumps(payload), content_type='application/json')
