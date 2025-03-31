from django.contrib import admin
from .models import Author, Genre, Book


admin.site.register(Author)
admin.site.register(Genre)


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    actions = ['delete_selected'] 
    
    
    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('books.can_edit_books')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('books.can_edit_books')
    
    
    
    def cover_preview(self, obj):
        if obj.cover:
            return f'<img src="{obj.cover.url}" width="50">'
        return "Нет обложки"
    cover_preview.allow_tags = True
    cover_preview.short_description = "Обложка"

admin.site.register(Book, BookAdmin)

