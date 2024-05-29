from django.urls import path
from userprofile import views


urlpatterns = [
    path('', views.create_user_profile),
    path('update/', views.update_user_profile)

]
