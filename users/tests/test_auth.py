from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class AuthTestCase(TestCase):
    def test_registration(self):
        """Тест регистрации нового пользователя"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
        })
        self.assertEqual(response.status_code, 302)  # Должен быть редирект
        self.assertTrue(User.objects.filter(username='testuser').exists())  # Пользователь создан

    def test_login(self):
        """Тест входа в систему"""
        user = User.objects.create_user(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123!',
        })
        self.assertEqual(response.status_code, 302)  # Должен быть редирект
        self.assertTrue('_auth_user_id' in self.client.session)  # Пользователь аутентифицирован

    def test_logout(self):
        """Тест выхода из системы"""
        user = User.objects.create_user(username='testuser', password='TestPassword123!')
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Должен быть редирект
        self.assertFalse('_auth_user_id' in self.client.session)  # Пользователь вышел

    def test_permission_denied_for_deleting_book(self):
        """Тест: обычный пользователь не может удалить книгу"""
        from books.models import Book

        user = User.objects.create_user(username='testuser', password='TestPassword123!')
        book = Book.objects.create(title='Test Book', author='Author')

        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('delete_book', args=[book.id]))

        self.assertEqual(response.status_code, 403)  # Ошибка доступа
