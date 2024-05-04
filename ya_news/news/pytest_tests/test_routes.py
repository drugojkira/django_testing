from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    [
        ('home_url', 'client', HTTPStatus.NOT_FOUND),
        ('login_url', 'client', HTTPStatus.NOT_FOUND),
        ('logout_url', 'client', HTTPStatus.NOT_FOUND),
        ('signup_url', 'client', HTTPStatus.NOT_FOUND),
        ('news_detail_url', 'client', HTTPStatus.NOT_FOUND),
        ('url_to_delete_comment', 'admin_client', HTTPStatus.NOT_FOUND),
        ('url_to_edit_comment', 'author_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_page_availability(url_fixture, client_fixture,
                           expected_status, request):
    client = request.getfixturevalue(client_fixture)
    response = client.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', 'id'),
        ('news:edit', 'id'),
    ),
)
def test_redirects(client, name, args, comment, login_url):
    url = reverse(name, args=(getattr(comment, args),))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
