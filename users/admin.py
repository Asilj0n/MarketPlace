from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'campus', 'whatsapp_number']
    list_filter = ['campus']
    search_fields = ['user__username', 'user__email', 'whatsapp_number']
