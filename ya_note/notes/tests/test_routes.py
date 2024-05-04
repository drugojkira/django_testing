from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .test_content import BaseTestCase

User = get_user_model()


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        for name in self.urls_without_args:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def page_available_for_authorized_user(self):
        for name, args in self.urls_with_args.items():
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_edit_delete_detail(self):
        users = [self.client_author, self.client_reader]
        statuses = [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        for user, status in zip(users, statuses):
            with self.subTest(user=user):
                response = user.get(self.notes_edit_url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = [
            ('notes:edit', (self.note.slug,), self.notes_edit_url),
            ('notes:delete', (self.note.slug,),
             reverse('notes:delete', args=(self.note.slug,))),
            ('notes:detail', (self.note.slug,),
             reverse('notes:detail', args=(self.note.slug,))),
            ('notes:list', None, reverse('notes:list')),
            ('notes:success', None, reverse('notes:success')),
            ('notes:add', None, reverse('notes:add')), ]

        for name, args, url in urls:
            with self.subTest(name=name):
                if args:
                    redirect_url = f'{self.login_url}?next={url}'
                else:
                    redirect_url = f'{self.login_url}?next={reverse(name)}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
