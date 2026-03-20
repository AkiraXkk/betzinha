from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^entrar/', views.LoginView.as_view(), name='login'),
    re_path(r'^sair/', views.logout, name='logout'),
    re_path(r'^cadastro/', views.CreateUserView.as_view(), name='cadastro'),
]
