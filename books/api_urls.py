from django.urls import path
from .views import BookListCreateView, BookDetailView, RegisterView, export_books_json, export_books_xml, export_books_yaml, import_books_json, import_books_xml, import_books_yaml, CachedBookListView, get_book_details
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('books/', BookListCreateView.as_view(), name='api_book_list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='api_book_detail'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),  # Получение токена по логину/паролю
    path('export/json/', export_books_json, name='export_books_json'),
    path('export/xml/', export_books_xml, name='export_books_xml'),
    path('export/yaml/', export_books_yaml, name='export_books_yaml'),
    path('import/json/', import_books_json, name='import_books_json'),
    path('import/xml/', import_books_xml, name='import_books_xml'),
    path('import/yaml/', import_books_yaml, name='import_books_yaml'),
    path('cached-books/', CachedBookListView.as_view(), name='cached_books'),
    path('book/<int:pk>/', get_book_details, name='book_details'),



]
