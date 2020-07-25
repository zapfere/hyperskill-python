from django.shortcuts import render, redirect
from django.views import View

from .models import Resume
from common.views import ItemCreationView
# Create your views here.


class ResumeListView(View):

    def get(self, request):
        resumes = Resume.objects.all()
        return render(request,
                      "resume/list.html",
                      context={"resumes": resumes})


class ResumeView(ItemCreationView):

    def _handle_post(self, request):
        Resume.objects.create(author=request.user,
                              description=request.POST["description"])
        return redirect("/home")
