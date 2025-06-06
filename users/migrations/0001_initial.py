# Generated by Django 5.1.3 on 2025-03-30 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("author", models.CharField(max_length=100)),
                ("genre", models.CharField(max_length=100)),
                ("published_date", models.DateField(blank=True, null=True)),
                (
                    "cover_image",
                    models.ImageField(blank=True, null=True, upload_to="covers/"),
                ),
            ],
        ),
    ]
