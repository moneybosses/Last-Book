import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    """Фильтр для книг"""
    title = django_filters.CharFilter(lookup_expr='icontains')  # Поиск по названию
    author = django_filters.CharFilter(lookup_expr='icontains')  # Поиск по автору

    class Meta:
        model = Book
        fields = ['title', 'author']
