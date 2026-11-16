from django.urls import path

from . import views

urlpatterns = [
    path('catalogo/', views.catalog_view, name='catalog'),
    path('mis-experiencias/', views.experience_list_view, name='experience_list'),
    path('experiencias/crear/', views.experience_create_view, name='experience_create'),
    path('experiencias/<int:pk>/editar/', views.experience_update_view, name='experience_update'),
    path('experiencias/<int:pk>/eliminar/', views.experience_delete_view, name='experience_delete'),
    path('categorias/', views.category_list_view, name='category_list'),
    path('categorias/crear/', views.category_create_view, name='category_create'),
    path('categorias/<int:pk>/editar/', views.category_update_view, name='category_update'),
    path('categorias/<int:pk>/eliminar/', views.category_delete_view, name='category_delete'),
    path('experiencias/<int:pk>/inscribirse/', views.reservation_create_view, name='reservation_create'),
    path('reservas/', views.reservation_list_view, name='reservation_list'),
    path('reservas/<int:pk>/estado/', views.reservation_status_update_view, name='reservation_status_update'),
]
