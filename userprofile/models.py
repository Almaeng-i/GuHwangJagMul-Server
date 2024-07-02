from django.core.exceptions import ValidationError
from django.db import DataError
from django.db import models
from accounts.models import CustomUser
from django.conf import settings


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_profiles')
    nickname = models.CharField(max_length=10)
    profile_picture_url = models.URLField(max_length=200, blank=True)
    user_introduction = models.CharField(max_length=50, null=True)
    
    def clean(self):
        if not self.nickname or not self.nickname.strip():
            raise ValidationError('닉네임 필드를 비워두거나 공백만 포함할 수 없습니다.')
        