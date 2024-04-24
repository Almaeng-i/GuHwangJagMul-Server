from django.contrib import admin
from django.urls import path
from accounts import views
import jwt



urlpatterns = [
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/login/callback/', views.KakaoCallbackView.as_view(), name='kakao_callback'),
    path('token/refresh/', views.reissue_token, name='reissued_token')
]
