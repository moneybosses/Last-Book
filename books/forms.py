from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genres', 'cover', 'published_date']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'genres': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }