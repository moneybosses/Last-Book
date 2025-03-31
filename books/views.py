from django.shortcuts import render, get_object_or_404, redirect
from .models import Book
from .forms import BookForm
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import generics,filters
from .serializers import BookSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsLibrarianOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BookFilter
import json
import yaml
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize,deserialize
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
import logging
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

logger = logging.getLogger(__name__)

def get_book(request, pk):
    try:
        book = Book.objects.get(pk=pk)
        return JsonResponse({'title': book.title, 'author': book.author})
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


class BookListCreateView(generics.ListCreateAPIView):
    """Список книг с фильтрацией и поиском"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author']
    ordering_fields = ['title', 'author']

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр одной книги, редактирование - только библиотекарям"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    
class RegisterView(APIView):
    """Регистрация пользователей"""
    permission_classes = [AllowAny]  # Доступно без авторизации

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=400)
    
    
def export_books_json(request):
    """Экспорт книг в JSON"""
    books = Book.objects.all()
    data = serialize("json", books)
    return HttpResponse(data, content_type="application/json")

def export_books_xml(request):
    """Экспорт книг в XML"""
    books = Book.objects.all()
    data = serialize("xml", books)
    return HttpResponse(data, content_type="application/xml")

def export_books_yaml(request):
    """Экспорт книг в YAML"""
    books = Book.objects.all()
    data = serialize("json", books)  # Django не поддерживает YAML напрямую
    yaml_data = yaml.dump(json.loads(data))
    return HttpResponse(yaml_data, content_type="application/x-yaml")

def import_books_json(request):
    """Импорт книг из JSON"""
    if request.method == "POST":
        data = json.loads(request.body)
        for obj in deserialize("json", json.dumps(data)):
            obj.save()
        return HttpResponse("JSON импортирован!", status=201)

def import_books_xml(request):
    """Импорт книг из XML"""
    if request.method == "POST":
        data = request.body.decode('utf-8')
        for obj in deserialize("xml", data):
            obj.save()
        return HttpResponse("XML импортирован!", status=201)

def import_books_yaml(request):
    """Импорт книг из YAML"""
    if request.method == "POST":
        data = yaml.safe_load(request.body)
        for obj in deserialize("json", json.dumps(data)):
            obj.save()
        return HttpResponse("YAML импортирован!", status=201)
    
    
class CachedBookListView(generics.ListAPIView):
    """Список книг с кешированием"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @method_decorator(cache_page(60 * 15))  # Кешируем на 15 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    

def get_book_details(request, pk):
    """Получение информации о книге с кешированием"""
    key = f'book_{pk}'
    book = cache.get(key)

    if not book:
        book = Book.objects.get(pk=pk)
        cache.set(key, book, timeout=60 * 10)  # Кеш на 10 минут

    return JsonResponse({"title": book.title, "author": book.author})



@extend_schema(
    summary="Получить список книг",
    description="Возвращает список всех книг в библиотеке.",
    responses={200: "application/json"},
)
@api_view(["GET"])
def book_list_api(request):
    books = ["Книга 1", "Книга 2", "Книга 3"]
    return Response({"books": books})
