from django.contrib import admin
from .models import StoryComments, Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')


admin.site.register(StoryComments)