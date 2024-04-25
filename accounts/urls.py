from django.contrib import admin
from django.urls import path
from accounts import views
import jwt



urlpatterns = [
    path('kakao/login/', views.kakao_login),
    path('kakao/login/callback/', views.KakaoCallbackView.as_view()),
    path('token/refresh/', views.reissue_token)
]
