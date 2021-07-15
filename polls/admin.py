from django.contrib import admin
from .models import PollComments, PollOptions, Poll


admin.site.register(PollComments)
admin.site.register(Poll)
admin.site.register(PollOptions)
