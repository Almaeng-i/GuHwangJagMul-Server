from django.contrib import admin
from django.urls import path
from accounts import views
import jwt



urlpatterns = [
    path('kakao/login/', views.kakao_login),
    path('reissue-token/', views.reissue_token),
    path('logout/', views.logout),
    path('my/', views.delete_user),
    path('save-device-token/', views.save_device_token)
]
