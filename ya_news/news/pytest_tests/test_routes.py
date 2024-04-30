from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', 'news'),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args, news):
    url = reverse(name, args=(news.pk,) if args == 'news' else None)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_pages_availability_for_author(author_client, name, comment):
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    [
        ('news:delete', pytest.lazy_fixture('admin_client'),
         HTTPStatus.NOT_FOUND),
        ('news:edit', pytest.lazy_fixture('author_client'),
         HTTPStatus.OK)
    ]
)
def test_pages_availability_for_different_users(reverse_url,
                                                parametrized_client,
                                                expected_status, comment):
    url = reverse(reverse_url, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', 'id'),
        ('news:edit', 'id'),
    ),
)
def test_redirects(client, name, args, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(getattr(comment, args),))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
