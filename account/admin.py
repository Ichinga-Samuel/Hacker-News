from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ["email", 'username', "verified", "is_admin", 'karma', 'about']
    list_filter = ["is_admin", 'verified',]
    fieldsets = [
        (None, {"fields": ["email", 'username', 'verified', 'karma', "password"]}),
        ("Personal info", {"fields": ["about"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "username", "password1", "password2", 'about', 'verified'],
            },
        ),
    ]
    search_fields = ["email", 'username']
    ordering = ["email"]
    filter_horizontal = []


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
