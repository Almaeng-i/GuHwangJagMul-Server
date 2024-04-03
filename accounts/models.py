from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

# Create your models here.
class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True, unique=True)
    username = None
    email = models.EmailField(_('email address'), unique=True)
    nickname = models.CharField(_('nickname'), max_length=50, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    social_provider = models.CharField(max_length=100, blank=True)
    social_uid = models.CharField(max_length=255, blank=True)
    is_social_user = models.BooleanField(default=False)

    def __str__(self):
        return self.email
