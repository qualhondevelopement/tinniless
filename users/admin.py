from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from django.contrib.auth.admin import UserAdmin


admin.site.unregister(Group)

# Register your models here.
class UserAccountAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'user_type', 'business', 'dob', 'is_active', 'is_email_verified')
    list_filter = ('user_type', 'business', 'is_active', 'is_email_verified')
    search_fields = ('username', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'dob', 'business', 'prefered_time_zone')}),
        ('Permissions', {'fields': ('is_active', 'is_email_verified', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Business)
# admin.site
# admin.site.register(CardDetails)