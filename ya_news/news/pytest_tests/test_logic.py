from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {
    'text': 'Новый техт'
}


def test_user_can_create_comment(author_client, author, news, news_detail_url):
    comments_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=FORM_DATA)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comments_count + 1
    new_comment = Comment.objects.last()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_note(client, login_url, news_detail_url):
    comments_count = Comment.objects.count()
    response = client.post(news_detail_url, data=FORM_DATA)
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count


def test_user_cant_use_bad_words(author_client, news_detail_url):
    comments_count = Comment.objects.count()
    form_data = FORM_DATA.copy()
    form_data['text'] = f'{BAD_WORDS[0]} текст'
    response = author_client.post(news_detail_url, data=form_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == comments_count


def test_author_can_delete_comment(author_client, news_detail_url,
                                   url_to_delete_comment):
    comments_count = Comment.objects.count()
    url_to_comments = news_detail_url + '#comments'
    response = author_client.delete(url_to_delete_comment)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count - 1


def test_author_can_edit_comment(author, author_client, comment, news,
                                 news_detail_url, url_to_edit_comment):
    url_to_comments = news_detail_url + '#comments'
    response = author_client.post(url_to_edit_comment, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_delete_comment_of_another_user(reader_client,
                                                  url_to_delete_comment):
    comments_count = Comment.objects.count()
    response = reader_client.delete(url_to_delete_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment, url_to_edit_comment
):
    initial_comment_text = comment.text
    response = reader_client.post(url_to_edit_comment, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    expected_comment = Comment.objects.get(id=comment.id)
    assert expected_comment.text == initial_comment_text
    assert expected_comment.author == comment.author
    assert expected_comment.news == comment.news
