from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('start/', views.auth_choice, name='auth_choice'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('scan/', views.scan, name='scan'),
    path('logout/', views.user_logout, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
