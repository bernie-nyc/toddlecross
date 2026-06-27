from django.contrib import admin
from .models import SyncJob, SyncSchedule
from django.utils import timezone
from croniter import croniter

# This class configures how our SyncJob model is displayed in Django admin.
@admin.register(SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    # These are the columns displayed in the admin list view.
    list_display = ('id', 'status', 'start_time', 'end_time', 'created_count', 'updated_count', 'deleted_count')
    # These filters allow admins to narrow down jobs by status or starting time.
    list_filter = ('status', 'start_time')
    # The default sorting order is newest jobs first.
    ordering = ('-start_time',)


# This class configures how our SyncSchedule model is displayed in Django admin.
@admin.register(SyncSchedule)
class SyncScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'cron_expression', 'sync_type', 'is_active', 'last_run', 'get_next_run')
    list_filter = ('is_active', 'sync_type')
    ordering = ('name',)

    def get_next_run(self, obj):
        if not obj.is_active:
            return "-"
        try:
            cron = croniter(obj.cron_expression, timezone.now())
            next_run = cron.get_next(timezone.datetime)
            # Make sure it displays nicely formatted
            return next_run.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "Invalid expression"
    get_next_run.short_description = 'Next Scheduled Run'

