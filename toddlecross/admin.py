from django.contrib import admin
from .models import SyncJob

# This class configures how our SyncJob model is displayed in Django admin.
@admin.register(SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    # These are the columns displayed in the admin list view.
    list_display = ('id', 'status', 'start_time', 'end_time', 'created_count', 'updated_count', 'deleted_count')
    # These filters allow admins to narrow down jobs by status or starting time.
    list_filter = ('status', 'start_time')
    # The default sorting order is newest jobs first.
    ordering = ('-start_time',)

