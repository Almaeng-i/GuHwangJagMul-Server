from django.contrib import admin
from django.urls import path
from accounts import views
import jwt



urlpatterns = [
    path('', views.kakao_login, name='kakao_login'),
    path('callback/', views.KakaoCallbackView.as_view(), name='kakao_callback'),
]
