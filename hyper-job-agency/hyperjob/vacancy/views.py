from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.views import View

from .models import Vacancy
from common.views import ItemCreationView


# Create your views here.
class VacancyListView(View):

    def get(self, request):
        vacancies = Vacancy.objects.all()
        return render(request,
                      "vacancy/list.html",
                      context={"vacancies": vacancies})


class VacancyView(ItemCreationView):

    def _handle_post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden()

        Vacancy.objects.create(author=request.user,
                               description=request.POST["description"])
        return redirect("/home")
