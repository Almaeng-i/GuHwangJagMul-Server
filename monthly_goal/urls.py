from django.urls import path,include
from monthly_goal import views

urlpatterns = [
    path('',views.create_month_list),
    path('update/', views.update_month_list),
    path('is-success/', views.is_success),
    path('delete/', views.delete_month_list),
    path('my/', views.get_my_month_list)
]
