from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

FORM_DATA = {
    'text': 'Новый техт'
}


def test_home_page(client, bulk_news_creation, home_url):
    response = client.get(home_url)
    news_list = response.context['object_list']
    news_count = news_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, bulk_news_creation, home_url):
    response = client.get(home_url)
    news_list = response.context['object_list']
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_detail_page_contains_form(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url, data=FORM_DATA)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)


def test_detail_page_contains_form_for_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_comments_order(client, news, commets):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_date_created = [comment.created for comment in all_comments]
    sorted_date = sorted(all_date_created)
    assert all_date_created == sorted_date
