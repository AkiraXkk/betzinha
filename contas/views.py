from django.contrib import messages
from django.contrib.auth import views as auth_user
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic


class LoginView(generic.FormView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _('Login successful!'))
        return reverse('partidas:home')


class CreateUserView(generic.CreateView):
    model = User
    fields = ['first_name', 'username', 'email', 'password']
    template_name = 'accounts/register.html'

    def get_success_url(self):
        messages.success(self.request, _('Registered user successful!'))
        return reverse('partidas:home')


def logout(request):
    auth_logout(request)
    return redirect('partidas:home')
