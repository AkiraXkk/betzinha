from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.MatchListView.as_view(), name='home'),
    re_path(r'^odds/feed/$', views.MatchOddsFeedView.as_view(), name='odds-feed'),
]
