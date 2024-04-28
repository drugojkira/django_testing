from django.conf import settings

from news.forms import CommentForm

FORM_DATA = {
    'text': 'Новый техт'
}


def test_home_page(client, bulk_news_creation, home_url):
    response = client.get(home_url)
    home_page_news = response.context['object_list']
    news_count = home_page_news.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, bulk_news_creation, home_url):
    response = client.get(home_url)
    ordered_news = response.context['object_list']
    all_dates = [news.date for news in ordered_news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_detail_page_contains_form(author_client, news, news_detail_url):
    response = author_client.get(news_detail_url, data=FORM_DATA)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)


def test_detail_page_contains_form_for_user(client, news, news_detail_url):
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_comments_order(client, news, comments, news_detail_url):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_date_created = [comment.created for comment in all_comments]
    sorted_date = sorted(all_date_created)
    assert all_date_created == sorted_date
