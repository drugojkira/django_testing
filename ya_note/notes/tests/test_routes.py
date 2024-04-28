from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.client_author = cls.client_class()
        cls.client_reader = cls.client_class()
        cls.urls_without_args = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        cls.urls_with_args = {
            'notes:list': (None,),
            'notes:success': (None,),
            'notes:add': (None,),
        }

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
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_edit_delite_detail(self):
        users = [self.client_author, self.client_reader]
        statuses = [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        for user, status in zip(users, statuses):
            with self.subTest(user=user):
                url = reverse('notes:edit', args=(self.note.slug,))
                user.force_login(self.author if
                                 user == self.client_author
                                 else self.reader)
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
