from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNotesPage(TestCase):

    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
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
        self.client.force_login(self.author)

    def test_notes_list(self):
        response = self.client.get(self.NOTES_URL)
        notes = response.context['object_list']
        first_note = notes[0]
        self.assertIn(first_note, notes)

    def test_reader_context_list(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        author_note = Note.objects.create(author=self.reader,
                                          title="Заметка читателя")
        self.assertNotIn(author_note, object_list)

    def test_author_context_list(self):
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        self.assertTrue(object_list)
        for note in object_list:
            self.assertEqual(note.author, self.author)


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
