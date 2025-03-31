from django.urls import path, include
from .views import book_list,  book_detail, add_book,  edit_book, delete_book

urlpatterns = [
    path('', book_list, name='book_list'),
    path('book/<int:book_id>/', book_detail, name='book_detail'),  # Новый маршрут
    path('add/', add_book, name='add_book'),  # Новый маршрут
    path('book/<int:book_id>/edit/', edit_book, name='edit_book'),  # Новый маршрут
    path('book/<int:book_id>/delete/', delete_book, name='delete_book'),
    path('api/', include('books.api_urls')),  # Подключаем API маршруты


]
