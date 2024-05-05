from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.client_author = cls.client_class()
        cls.client_reader = cls.client_class()
        cls.client_author.force_login(cls.author)
        cls.client_reader.force_login(cls.reader)
        cls.list_url = reverse('notes:list')
        cls.note = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            author=cls.author
        )
        cls.note_url = reverse('notes:success', args=None)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': 'Измененный текст',
            'title': 'Измененный заголовок'
        }
        cls.url = reverse('notes:add', args=None)
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': 'Текст',
            'title': 'Заголовок'
        }
        cls.urls = {
            'edit': reverse('notes:edit', args=(cls.note.slug,)),
            'add': reverse('notes:add'),
        }
        cls.urls_without_args = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        cls.urls_with_args = {
            'list': reverse('notes:list'),
            'success': reverse('notes:success'),
            'add': reverse('notes:add'),
        }
        cls.login_url = reverse('users:login')
        cls.notes_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_detail = reverse('notes:detail', args=(cls.note.slug,))


class TestNotesPage(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.notes = [
            Note(
                title=f'Новость{index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'note-{index}'
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(cls.notes)

    def test_notes_list(self):
        response = self.author_client.get(self.list_url)
        notes = response.context['object_list']
        author_note = Note.objects.filter(author=self.author).first()
        self.assertIsNotNone(author_note)
        self.assertIn(author_note, notes)

    def test_reader_context_list(self):
        response = self.author_client.get(self.list_url)
        notes_queryset = response.context['object_list']
        self.assertFalse(notes_queryset.filter(author=self.reader).exists())


class TestAddAndEditPage(BaseTestCase):

    def test_form(self):
        for name, url in self.urls.items():
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
