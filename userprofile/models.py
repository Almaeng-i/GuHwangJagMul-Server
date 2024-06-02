from django.db import models
from accounts.models import CustomUser
from django.conf import settings


# Create your models here.
class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_profiles')
    profile_picture_url = models.URLField(max_length=200, blank=True)
    user_introduction = models.CharField(max_length=50)
    
   