from django.urls import path
from userprofile import views


urlpatterns = [
    path('', views.save_user_profile)
]
