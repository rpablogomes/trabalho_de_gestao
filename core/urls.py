from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html', next_page='dashboard'), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('operations/', views.operations_view, name='operations'),
    path('operations/<uuid:op_id>/reverse/', views.reverse_operation, name='reverse_operation'),
]