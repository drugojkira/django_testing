from datetime import timedelta

from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

import pytest

from news.models import Comment, News


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def bulk_news_creation(author):
    return News.objects.bulk_create(
        News(title=f'Новость {index}', text='Просто текст.')
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comments(author, news):
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_to_delete_comment(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_to_edit_comment(comment):
    return reverse('news:edit', args=(comment.id,))
