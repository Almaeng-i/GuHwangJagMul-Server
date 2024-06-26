from django.core.exceptions import ValidationError
from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Todo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='todo')
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=False, null=False)
    is_succeed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
        
    def clean(self):
        if self.title is None or self.title.strip() == "":
            raise ValidationError('todo를 비워두거나 공백만 포함할 수 없습니다.')
