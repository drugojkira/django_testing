from http import HTTPStatus

import pytest
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
    'fixture_name',
    [
        'url_to_delete_comment',
        'url_to_edit_comment',
    ],
)
def test_redirects(client, fixture_name, login_url, request):
    url_fixture = request.getfixturevalue(fixture_name)
    response = client.get(url_fixture)
    expected_url = f'{login_url}?next={url_fixture}'
    assertRedirects(response, expected_url)
