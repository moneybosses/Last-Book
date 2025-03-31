from django.test import TestCase
from django.urls import reverse
from books.models import Book, Author, Genre
from datetime import date

class BookTestCase(TestCase):
    def setUp(self):
        """Создаём тестового автора, жанр и книгу"""
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.genre = Genre.objects.create(name="Science Fiction")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            published_date=date(2020, 5, 17)
        )
        self.book.genres.add(self.genre)  # Добавляем жанр к книге

    def test_book_creation(self):
        """Проверяем, что книга создаётся корректно"""
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author.first_name, "John")
        self.assertEqual(self.book.author.last_name, "Doe")
        self.assertEqual(self.book.published_date, date(2020, 5, 17))
        self.assertIn(self.genre, self.book.genres.all())

    def test_book_list_view(self):
        """Проверяем, что список книг открывается"""
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")

    def test_book_create_view(self):
        """Тестируем создание книги через форму"""
        response = self.client.post(reverse('create_book'), {
            'title': 'New Book',
            'author': self.author.id,  # Передаём ID автора
            'genres': [self.genre.id],  # Передаём ID жанра
            'published_date': '2023-07-15',
        })
        self.assertEqual(response.status_code, 302)  # Должен быть редирект
        self.assertTrue(Book.objects.filter(title='New Book').exists())

    def test_book_delete_view(self):
        """Тестируем удаление книги"""
        response = self.client.post(reverse('delete_book', args=[self.book.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
