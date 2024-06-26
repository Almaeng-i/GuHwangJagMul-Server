from django.contrib import admin
from django.urls import path,include
from todo import views

urlpatterns = [
    path('',views.create_todo),
    path('update/', views.update_todo),
    path('is-success/', views.is_success),
    path('delete/', views.delete_todo),
    path('my/',views.get_my_todo_list)
    
]

