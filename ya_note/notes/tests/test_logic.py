from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add', args=None)
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': 'Текст',
            'title': 'Заголовок'
        }

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_user_can_create_note(self):
        notes_count_before = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before + 1, notes_count_after)
        last_note = Note.objects.last()
        self.assertEqual(last_note.text, self.form_data['text'])
        self.assertEqual(last_note.title, self.form_data['title'])
        self.assertEqual(last_note.author, self.user)

    def test_two_identical_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)
        form = response.context['form']
        slug_errors = form.errors.get('slug', [])
        self.assertTrue(slug_errors)

    def test_automatic_creation_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.note_url = reverse('notes:success', args=None)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': 'Измененный текст',
            'title': 'Измененный заголовок'
        }

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        notes_count_after = Note.objects.count()
        self.assertRedirects(response, self.note_url)
        self.assertEqual(notes_count_before - 1, notes_count_after)

    def test_user_cant_delete_note_of_another_user(self):
        notes_count_before = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count_before, notes_count_after)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.note_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.text, self.note.text)
        self.assertEqual(edited_note.title, self.note.title)
        self.assertEqual(edited_note.author, self.note.author)
