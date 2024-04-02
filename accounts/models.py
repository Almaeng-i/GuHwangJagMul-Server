from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from allauth.socialaccount.models import SocialAccount


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    social_provider = models.CharField(max_length=100, blank=True)
    social_uid = models.CharField(max_length=255, blank=True)
    is_social_user = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class SocialProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    social_account = models.OneToOneField(SocialAccount, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.user.is_social_user = True  # 소셜 사용자로 표시
        self.user.save()
        super().save(*args, **kwargs)
