from django.contrib import admin
from django.urls import path
from almaengI import views


urlpatterns = [
    path('', views.save_almaengi),
    path('mycollection/', views.response_almaengi_info)
]
