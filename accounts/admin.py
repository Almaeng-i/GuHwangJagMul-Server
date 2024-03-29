from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'email')  # 이 부분을 추가합니다.

admin.site.register(CustomUser, CustomUserAdmin)
TokenAdmin.raw_id_fields = ('user',)
