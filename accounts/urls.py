from django.contrib import admin
from django.urls import path
from accounts import views

urlpatterns = [
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('login/kakao/callback/', views.KakaoCallbackView.as_view(), name='kakao_callback'),
    # path('kakao/login/finish/', views.KakaoLogin.as_view(), name='kakao_login_todjango'),  # 일단 사용하지 않음으로 주석처리
]
