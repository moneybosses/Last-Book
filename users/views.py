from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from books.models import Book
from .forms import BookForm, RegisterForm
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def register(request):

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_group, _ = Group.objects.get_or_create(name='Пользователь')
            user.groups.add(user_group)  # Добавляем нового пользователя в группу
            login(request, user)
            return redirect('book_list')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

@login_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

def setup_groups():
    admin_group, _ = Group.objects.get_or_create(name='Администратор')
    user_group, _ = Group.objects.get_or_create(name='Пользователь')

setup_groups()  # Создаём группы при старте сервера

def setup_permissions():
    content_type = ContentType.objects.get_for_model(Book)
    delete_permission, _ = Permission.objects.get_or_create(
        codename='delete_book', 
        name='Can delete book',
        content_type=content_type
    )

    admin_group = Group.objects.get(name='Администратор')
    admin_group.permissions.add(delete_permission)

setup_permissions()  # Создаём права при старте сервера
