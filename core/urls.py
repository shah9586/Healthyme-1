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
    path('admin-dashboard/', views.admin_dashboard),
    path('delete-user/<int:user_id>/', views.delete_user),
    path('edit-user/<int:user_id>/', views.edit_user), 
    #path('scan/', views.scan_product, name='scan')
    path("rewards/", views.rewards_page, name="rewards"),
    path("health-score/", views.health_score_page, name="health_score"),
    path("ingredients/", views.ingredients_page, name="ingredients"),
    path("rewards/", views.rewards_page, name="rewards"),
    path("community/", views.community, name="community"),
]
