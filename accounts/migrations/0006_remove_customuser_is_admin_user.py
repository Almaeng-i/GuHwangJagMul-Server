# Generated by Django 5.0.3 on 2024-04-03 06:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_customuser_is_admin_user_alter_customuser_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="is_admin_user",
        ),
    ]