from django.contrib import admin

from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'campus', 'status', 'created_at']
    list_filter = ['status', 'category', 'campus', 'condition']
    search_fields = ['title', 'description', 'seller__username', 'seller__email']
    list_editable = ['status']
