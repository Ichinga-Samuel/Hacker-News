from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UA
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'about')
    ordering = ('-created',)


# admin.site.unregister(User)
# admin.site.register(UserAdmin, UA)
