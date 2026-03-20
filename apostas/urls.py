from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^realizar/', views.BetCreateView.as_view(), name='realizar-aposta'),
]
