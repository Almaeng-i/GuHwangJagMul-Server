from django.urls import path
from userprofile import views


urlpatterns = [
    path('', views.create_user_profile),
    path('my/', views.response_userprofile),
    path('update/', views.update_user_profile),

]
