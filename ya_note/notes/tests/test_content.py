from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

from notes.forms import NoteForm

User = get_user_model()


class TestNotesPage(TestCase):

    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        all_notes = [
            Note(
                title=f'Новость{index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'note-{index}'
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(all_notes)

    def setUp(self):
        self.client = self.author_client
        self.reader_client = self.reader_client

    def test_notes_list(self):
        response = self.client.get(self.NOTES_URL)
        notes = response.context['object_list']
        first_note = notes[0]
        self.assertIn(first_note, notes)

    def test_reader_context_list(self):
        response = self.client.get(self.NOTES_URL)
        notes_queryset = response.context['object_list']
        author_note = Note.objects.create(author=self.reader,
                                          title="Заметка читателя")
        self.assertNotIn(author_note, notes_queryset)


class TestAddAndEditPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.notes = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            author=cls.author
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.author)

    def test_form(self):
        urls = (
            ('notes:edit', (self.notes.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
