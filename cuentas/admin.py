from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, UserRole
# Register your models here.

class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    inlines = [UserRoleInline]
    
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'administrador', 'guia', 'operador', 'turista', 'cliente')
    list_filter = ('administrador', 'guia', 'operador', 'turista', 'cliente')
    search_fields = ('role_name',)
    
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'role')
    list_filter = ('role',)
    search_fields = ('user_id__username', 'role__role_name')