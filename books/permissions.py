from rest_framework import permissions

class IsLibrarianOrReadOnly(permissions.BasePermission):
    """Разрешает изменение книг только библиотекарям, а чтение — всем"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Чтение разрешено всем
        return request.user.has_perm('books.can_edit_books')  # Изменять могут только библиотекари
