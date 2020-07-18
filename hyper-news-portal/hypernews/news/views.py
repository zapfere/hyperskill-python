from typing import Dict
from json import load, dump

from django.shortcuts import redirect, render
from django.conf import settings
from django.views import View
from django.http import Http404

from .models import NewsItem, NewsItemEncoder
from .models import add_news_item, filter_news_by_title, \
    list_to_dict, to_date_dict


class RootView(View):

    def get(self, request, *args, **kwargs):
        return redirect("/news/")


class NewsListView(View):

    def get(self, request, *args, **kwargs):

        search_str = request.GET.get("q")
        print(search_str)
        if search_str:
            data = filter_news_by_title(search_str, news_by_day)
        else:
            data = news_by_day

        context = {"data": data}
        return render(request, "news_list.html", context=context)


class NewsItemView(View):

    def get(self, request, news_id, *args, **kwargs):

        if news_data.get(news_id) is None:
            raise Http404

        context = {"news_obj": news_data[news_id]}
        return render(request, "news_item.html", context=context)


class NewsAddView(View):

    def get(self, request, *args, **kwargs):

        return render(request, "news_add_item.html")

    def post(self, request, *args, **kwargs):

        add_news_item(request.POST["title"], request.POST["text"], news_data)
        refresh_news_by_day()
        save_news_data()
        return redirect("/news/")


def load_news_data() -> Dict[int, NewsItem]:

    try:
        with open(settings.NEWS_JSON_PATH) as news_data_file:
            loaded = load(news_data_file)

        return list_to_dict(loaded)

    except FileNotFoundError:
        print("File not found! " + settings.NEWS_JSON_PATH)
        return dict()


def save_news_data() -> None:

    with open(settings.NEWS_JSON_PATH, "w") as news_data_file:
        dump(list(news_data.values()), news_data_file, cls=NewsItemEncoder)


def refresh_news_by_day() -> None:

    global news_by_day
    news_by_day = to_date_dict(news_data.values())


news_by_day = []
news_data = load_news_data()
refresh_news_by_day()
