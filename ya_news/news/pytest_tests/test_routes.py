from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url_fixture',
    [
        'home_url',
        'login_url',
        'logout_url',
        'signup_url',
        'news_detail_url',
    ],
)
def test_pages_availability_for_anonymous_user(client, url_fixture):
    response = client.get(url_fixture)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_pages_availability_for_author(author_client, name, comment):
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    [
        ('news:delete', pytest.lazy_fixture('admin_client'),
         HTTPStatus.NOT_FOUND),
        ('news:edit', pytest.lazy_fixture('author_client'),
         HTTPStatus.NOT_FOUND)
    ]
)
def test_pages_availability_for_different_users(reverse_url,
                                                parametrized_client,
                                                status):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


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
