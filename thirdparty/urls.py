from django.db import models
from thirdparty import views
from django.conf import settings
from django.urls import path



urlpatterns = [
    path('img-upload/', views.receive_img)
]
