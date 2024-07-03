from django.contrib import admin
from django.urls import path
from accounts import views
import jwt



urlpatterns = [
    path('kakao/login/', views.kakao_login),
    path('kakao/login/callback/', views.KakaoCallbackView.as_view()),
    path('reissue-token/', views.reissue_token),
    path('logout/', views.logout),
    path('my/', views.delete_user)
]
