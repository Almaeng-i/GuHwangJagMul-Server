# Generated by Django 4.2.13 on 2024-07-27 08:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Character",
            fields=[
                (
                    "id",
                    models.AutoField(primary_key=True, serialize=False, unique=True),
                ),
                ("character_type", models.CharField(max_length=20)),
                ("name", models.CharField(max_length=20)),
                ("level", models.PositiveBigIntegerField(default=1)),
                ("exp", models.PositiveBigIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="characters",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
