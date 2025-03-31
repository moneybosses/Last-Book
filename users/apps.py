from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
     from .views import setup_groups, setup_permissions
     setup_groups()
     setup_permissions()