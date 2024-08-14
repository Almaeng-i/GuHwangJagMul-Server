from django.urls import path
from alarm import views

urlpatterns = [
    path('push/', views.send_push_notification),
]
