from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Character(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='characters')
    id = models.AutoField(primary_key=True, unique=True)
    character_type = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    level = models.PositiveBigIntegerField(default=1)
    exp = models.PositiveBigIntegerField(default=0)
    
    def __str__(self):
        return self.id
    