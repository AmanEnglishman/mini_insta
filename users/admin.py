from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Profile

class UserAdmin(BaseUserAdmin):
    """Админка для кастомного пользователя"""
    list_display = ('id', 'email', 'username', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        (_('Important dates'), {'fields': ('last_login', )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


class ProfileAdmin(admin.ModelAdmin):
    """Админка для профили"""
    list_display = ('id', 'user', 'gender', 'created_at')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, UserAdmin)