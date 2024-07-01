from django.urls import path
from bucket_list import views


urlpatterns = [
    path('', views.create_bucket_list),
    path('update/', views.update_bucket_list),
    path('is-success/', views.is_success),
    path('delete/', views.delete_bucket_list),
    path('my/', views.get_my_bucket_list)
]
