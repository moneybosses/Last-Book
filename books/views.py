import logging
import json
import yaml

from django.core.cache import cache
from django.core.serializers import serialize, deserialize
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import generics, filters, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend

from .models import Book, Author, Genre
from .forms import BookForm
from .serializers import BookSerializer, AuthorSerializer, GenreSerializer, UserSerializer
from .permissions import IsLibrarianOrReadOnly
from .filters import BookFilter
from rest_framework.parsers import MultiPartParser, FormParser

logger = logging.getLogger(__name__)


# =================== WEB-ПРЕДСТАВЛЕНИЯ ===================

def get_book(request, pk):
    try:
        book = Book.objects.get(pk=pk)
        return JsonResponse({'title': book.title, 'author': str(book.author)})
    except Book.DoesNotExist:
        logger.error(f"Книга с ID {pk} не найдена")
        return JsonResponse({'error': 'Книга не найдена'}, status=404)


def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_detail.html', {'book': book})


@permission_required('books.add_book')
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Добавить книгу'})


@permission_required('books.change_book')
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Редактировать книгу'})


@permission_required('books.delete_book')
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        return redirect('book_list')
    return render(request, 'books/delete_confirm.html', {'book': book})


# =================== DRF API-ПРЕДСТАВЛЕНИЯ ===================

@extend_schema(tags=["Книги"])
class BookListCreateView(generics.ListCreateAPIView):
    """Список книг с фильтрацией и поиском"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'author__name']
    parser_classes = [MultiPartParser, FormParser]  # Добавьте эту строку


@extend_schema(tags=["Книги"])
class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр одной книги, редактирование - только библиотекарям"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]


@extend_schema(tags=["Пользователи"])
class RegisterView(APIView):
    """Регистрация пользователей"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=400)


# =================== ИМПОРТ / ЭКСПОРТ ===================

def export_books_json(request):
    books = Book.objects.all()
    data = serialize("json", books)
    return HttpResponse(data, content_type="application/json")


def export_books_xml(request):
    books = Book.objects.all()
    data = serialize("xml", books)
    return HttpResponse(data, content_type="application/xml")


def export_books_yaml(request):
    books = Book.objects.all()
    data = serialize("json", books)
    yaml_data = yaml.dump(json.loads(data))
    return HttpResponse(yaml_data, content_type="application/x-yaml")


def import_books_json(request):
    if request.method == "POST":
        data = json.loads(request.body)
        for obj in deserialize("json", json.dumps(data)):
            obj.save()
        return HttpResponse("JSON импортирован!", status=201)


def import_books_xml(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        for obj in deserialize("xml", data):
            obj.save()
        return HttpResponse("XML импортирован!", status=201)


def import_books_yaml(request):
    if request.method == "POST":
        data = yaml.safe_load(request.body)
        for obj in deserialize("json", json.dumps(data)):
            obj.save()
        return HttpResponse("YAML импортирован!", status=201)


# =================== КЕШИРОВАНИЕ ===================
@extend_schema(exclude=True)
class CachedBookListView(generics.ListAPIView):
    """Список книг с кешированием"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

def get_book_details(request, pk):
    """Получение информации о книге с кешированием"""
    key = f'book_{pk}'
    book = cache.get(key)

    if not book:
        book = Book.objects.get(pk=pk)
        cache.set(key, book, timeout=60 * 10)

    return JsonResponse({"title": book.title, "author": str(book.author)})


# =================== API ДЛЯ SWAGGER-ПРОВЕРКИ ===================

@extend_schema(
    summary="Получить список книг",
    description="Возвращает список всех книг в библиотеке.",
    responses={200: "application/json"},
    tags=["Swagger-Тест"]
)
@api_view(["GET"])
def book_list_api(request):
    books = ["Книга 1", "Книга 2", "Книга 3"]
    return Response({"books": books})


# =================== ViewSets ===================

@extend_schema_view(
    list=extend_schema(summary="Список книг", tags=["Книги"]),
    create=extend_schema(summary="Добавить книгу", tags=["Книги"]),
    retrieve=extend_schema(summary="Получить книгу", tags=["Книги"]),
    update=extend_schema(summary="Обновить книгу", tags=["Книги"]),
    partial_update=extend_schema(summary="Частичное обновление книги", tags=["Книги"]),
    destroy=extend_schema(summary="Удалить книгу", tags=["Книги"]),
)
@extend_schema_view(
    list=extend_schema(summary="Список книг", tags=["Книги"]),
    create=extend_schema(
        summary="Добавить книгу",
        tags=["Книги"],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'author_id': {'type': 'integer'},
                    'genre_ids': {'type': 'array', 'items': {'type': 'integer'}},
                    'cover': {'type': 'string', 'format': 'binary'},  # Ключевое изменение!
                    'published_date': {'type': 'string', 'format': 'date'},
                }
            }
        },
        responses={201: BookSerializer},
    ),
    retrieve=extend_schema(summary="Получить книгу", tags=["Книги"]),
    update=extend_schema(summary="Обновить книгу", tags=["Книги"]),
    partial_update=extend_schema(summary="Частичное обновление книги", tags=["Книги"]),
    destroy=extend_schema(summary="Удалить книгу", tags=["Книги"]),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'author__name']
    parser_classes = [MultiPartParser, FormParser]

@extend_schema_view(
    list=extend_schema(summary="Список авторов", tags=["Авторы"]),
    create=extend_schema(summary="Добавить автора", tags=["Авторы"]),
    retrieve=extend_schema(summary="Получить автора", tags=["Авторы"]),
    update=extend_schema(summary="Обновить автора", tags=["Авторы"]),
    partial_update=extend_schema(summary="Частичное обновление автора", tags=["Авторы"]),
    destroy=extend_schema(summary="Удалить автора", tags=["Авторы"]),
)
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsLibrarianOrReadOnly]


@extend_schema_view(
    list=extend_schema(summary="Список жанров", tags=["Жанры"]),
    create=extend_schema(summary="Добавить жанр", tags=["Жанры"]),
    retrieve=extend_schema(summary="Получить жанр", tags=["Жанры"]),
    update=extend_schema(summary="Обновить жанр", tags=["Жанры"]),
    partial_update=extend_schema(summary="Частичное обновление жанра", tags=["Жанры"]),
    destroy=extend_schema(summary="Удалить жанр", tags=["Жанры"]),
)
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsLibrarianOrReadOnly]

