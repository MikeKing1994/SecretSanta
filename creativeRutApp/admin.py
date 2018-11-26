from django.contrib import admin

from .models import ParticipantName, ParticipantEmail

admin.site.register(ParticipantName)
admin.site.register(ParticipantEmail)