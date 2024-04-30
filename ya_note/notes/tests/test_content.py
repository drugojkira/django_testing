from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')


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

    def setUp(self):
        super().setUp()
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_notes_list(self):
        response = self.author_client.get(reverse('notes:list'))
        notes = response.context['object_list']
        author_note = Note.objects.filter(author=self.author).first()
        self.assertIsNotNone(author_note)
        self.assertIn(author_note, notes)

    def test_reader_context_list(self):
        response = self.author_client.get(reverse('notes:list'))
        notes_queryset = response.context['object_list']
        self.assertNotIn(self.reader, [note.author for note in notes_queryset])


class TestAddAndEditPage(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            author=cls.author
        )

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.force_login(self.author)

    def test_form(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
