from typing import List, Dict, Iterable
from random import randint

from datetime import datetime
from json import JSONEncoder

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

# Create your models here.


class NewsItem:

    def __init__(self, item: Dict[str, object]):

        self.link = item["link"]  # mandatory
        self.created = item.get("created")
        self.title = item.get("title")
        self.text = item.get("text")

    def __repr__(self):
        return str(self.__dict__)


class NewsItemEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, NewsItem):
            return obj.__dict__
        return JSONEncoder.default(self, obj)


class NewsRecord:

    def __init__(self, date: str, news_items: List[NewsItem]):

        self.date = date
        self.news_items = news_items


def list_to_dict(list_data: List[Dict[str, object]]) -> Dict:

    result = dict()

    for entry in list_data:
        parsed = NewsItem(entry)
        result[parsed.link] = parsed

    return result


def to_date_dict(list_data: Iterable[NewsItem]) -> List[NewsRecord]:

    result = __fill_day_dict(list_data)

    result = (NewsRecord(date, news_items)
              for (date, news_items) in result.items())
    result = sorted(result, key=lambda x: x.date, reverse=True)

    return result


def add_news_item(title: str, text: str, items: Dict[int, NewsItem]) -> None:

    new_id = __generate_unique_id(items.keys())
    created = datetime.now().strftime(DATETIME_FORMAT)
    new_item = NewsItem({
        "link": new_id,
        "created": created,
        "title": title,
        "text": text
    })
    items[new_id] = new_item


def filter_news_by_title(search_str: str,
                         records: List[NewsRecord]) -> List[NewsRecord]:

    result = dict()
    for record in records:
        for item in record.news_items:
            if item.title and item.title.find(search_str) != -1:
                __add_item_to_record(item, record.date, result)

    return list(result.values())


def __fill_day_dict(list_data: Iterable[NewsItem]) -> Dict[str, NewsItem]:

    result = dict()

    for entry in list_data:
        day_date = datetime.strptime(entry.created, DATETIME_FORMAT)
        day_date = datetime.strftime(day_date, DATE_FORMAT)
        day_news = result.get(day_date, list())
        day_news.append(entry)
        result[day_date] = day_news

    return result


def __generate_unique_id(existing_ids: Iterable[int]) -> int:

    new_id = randint(1, 10000000)
    while new_id in existing_ids:
        new_id = randint(1, 10000000)

    return new_id


def __add_item_to_record(item: NewsItem,
                         day: str,
                         records: Dict[str, NewsRecord]):

    record = records.get(day)

    if record is None:
        record = NewsRecord(day, list())
        records[day] = record

    record.news_items.append(item)
