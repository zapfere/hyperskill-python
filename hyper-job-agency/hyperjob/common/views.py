from abc import ABCMeta
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.views import View
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect


class MyLoginView(LoginView):
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    template_name = 'common/login.html'


# Create your views here.
class CreateUserView(CreateView):
    form_class = UserCreationForm
    success_url = "/login"
    template_name = "common/signup.html"


class ItemCreationView(View, metaclass=ABCMeta):

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        return self._handle_post(request)

    def _handle_post(self, request):
        raise NotImplementedError


class ProfileView(View):

    def get(self, request):
        url = "/vacancy/new" if request.user.is_staff else "/resume/new"
        return render(request,
                      "common/profile.html",
                      context={"target_url": url})
