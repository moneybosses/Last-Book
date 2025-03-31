from django.db import models

# Модель автора
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Модель жанра
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Модель книги
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # Связь с автором
    genres = models.ManyToManyField(Genre,  blank=True)  # Связь многие-ко-многим с жанрами
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)  # Обложка книги
    published_date = models.DateField(null=True, blank=True)  # Дата публикации

    def __str__(self):
        return self.title

class Meta:
        permissions = [
            ("can_edit_books", "Can add, edit, and delete books"),
        ]