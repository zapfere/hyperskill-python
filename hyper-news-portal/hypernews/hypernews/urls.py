"""hypernews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from news.views import RootView, NewsAddView, NewsItemView, NewsListView


urlpatterns = [
    path("news/create/", NewsAddView.as_view()),
    path("news/<int:news_id>/", NewsItemView.as_view()),
    path("news/", NewsListView.as_view()),
    path("", RootView.as_view()),
    path("admin/", admin.site.urls)
]
urlpatterns += static(settings.STATIC_URL)
