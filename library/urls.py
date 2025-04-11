"""
URL configuration for library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from books.views import book_list  # Import book_list from the appropriate module

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', book_list, name='book_list'),

    # Web-маршруты
    path('', include('books.urls')),
    path('users/', include('users.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('silk/', include('silk.urls', namespace='silk')),
    path('set_language/', set_language, name='set_language'),

    # DRF Spectacular - OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    #path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # API endpoints (включаем только один раз)
    path('api/', include('books.api_urls')),
]

# Раздача медиа-файлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
