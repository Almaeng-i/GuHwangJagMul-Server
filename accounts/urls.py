from django.contrib import admin
from django.urls import path
from accounts import views
from .middleware import AccessTokenMiddleware
import jwt



urlpatterns = [
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('login/kakao/callback/', views.KakaoCallbackView.as_view(), name='kakao_callback'),
    path('test-api/', views.test_api, name='test_api'),
]
