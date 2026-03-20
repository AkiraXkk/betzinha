from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.MatchListView.as_view(), name='home'),
    url(r'^odds/feed/$', views.MatchOddsFeedView.as_view(), name='odds-feed'),
]
