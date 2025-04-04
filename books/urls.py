from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    book_list, book_detail, add_book, delete_book,
    BookViewSet, AuthorViewSet, GenreViewSet
)

# DRF router для ViewSet
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'genres', GenreViewSet, basename='genre')

urlpatterns = [
    # Web-представления
    path('', book_list, name='book_list'),
    path('book/<int:book_id>/', book_detail, name='book_detail'),
    path('add/', add_book, name='add_book'),
    path('book/<int:book_id>/delete/', delete_book, name='delete_book'),

    # API маршруты
    path('api/', include(router.urls)),

    
]
