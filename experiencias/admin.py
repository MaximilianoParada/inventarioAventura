from django.contrib import admin

from .models import Category, Experience, Reservation


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'creator', 'scheduled_at', 'capacity', 'is_active')
    list_filter = ('is_active', 'category', 'scheduled_at')
    search_fields = ('title', 'description', 'creator__username')
    date_hierarchy = 'scheduled_at'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience', 'reserved_at', 'payment_status')
    list_filter = ('payment_status', 'reserved_at')
    search_fields = ('user__username', 'experience__title')
    readonly_fields = ('reserved_at',)
