from django.urls import path    
from .import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('usuarios/', views.user_list_view, name='user_list'),
    path('usuarios/crear/', views.user_create_view, name='user_create'),
    path('usuarios/<int:pk>/editar/', views.user_update_view, name='user_update'),
]