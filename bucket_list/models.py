from django.db import models
from accounts.models import CustomUser
from django.core.exceptions import ValidationError

# Create your models here.
class BucketList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bucket_list')
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=200, blank=False, null=False)
    content = models.TextField(max_length=300, null=True)
    is_succeed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if not self.title or not self.title.strip():
            raise ValidationError('bucket list를 비워두거나 공백만 포함할 수 없습니다.')
