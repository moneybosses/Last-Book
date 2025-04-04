from rest_framework import serializers
from .models import Book, Author, Genre
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

# --- Author ---
class AuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

# --- Genre ---
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

# --- Book ---
class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True
    )

    genres = GenreSerializer(read_only=True, many=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), source='genres', many=True, write_only=True
    )

    class Meta:
        model = Book
        fields = [
            'id', 'title',
            'author', 'author_id',
            'genres', 'genre_ids',
            'cover', 'published_date'
        ]

# --- User ---
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# --- Регистрация пользователя ---
class RegisterView(APIView):
    """
    Регистрация нового пользователя.
    Возвращает токен после успешной регистрации.
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserSerializer,
        responses={201: {"type": "object", "properties": {"token": {"type": "string"}}}},
        summary="Регистрация нового пользователя",
        description="Позволяет создать нового пользователя и получить токен авторизации."
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=201)
        return Response(serializer.errors, status=400)
