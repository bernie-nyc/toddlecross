from django.core.management.base import BaseCommand
from toddlecross.models import SyncJob
from toddlecross.views import run_sync_job_background

class Command(BaseCommand):
    help = 'Executes the data sync pipeline synchronously and records execution metrics.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='both',
            help='Specify sync type: students, teachers, or both'
        )
        parser.add_argument(
            '--scheduled',
            action='store_true',
            help='Run in checking mode looking up and triggering active database sync schedules.'
        )

    def handle(self, *args, **options):
        is_scheduled = options.get('scheduled', False)
        
        if is_scheduled:
            from toddlecross.models import SyncSchedule
            from django.utils import timezone
            from croniter import croniter
            from datetime import datetime, timedelta
            
            now = timezone.now()
            self.stdout.write(f"Evaluating active schedules at {now}...")
            
            active_schedules = SyncSchedule.objects.filter(is_active=True)
            triggered_any = False
            
            for schedule in active_schedules:
                # Check if it was already run in the current minute (avoid duplicates)
                if schedule.last_run and (now - schedule.last_run) < timedelta(minutes=1):
                    continue
                
                try:
                    # Initialize croniter
                    cron = croniter(schedule.cron_expression, now)
                    prev_time = cron.get_prev(datetime)
                    
                    # If expected previous run matches the current minute, it is due!
                    if now.replace(second=0, microsecond=0) == prev_time.replace(second=0, microsecond=0):
                        self.stdout.write(f"Schedule '{schedule.name}' is due to run. Triggering '{schedule.sync_type}' sync.")
                        
                        # Create and run the SyncJob synchronously
                        job = SyncJob.objects.create(status='Pending', sync_type=schedule.sync_type)
                        run_sync_job_background(job.id)
                        
                        # Update last run
                        schedule.last_run = now
                        schedule.save()
                        triggered_any = True
                except Exception as e:
                    self.stderr.write(f"Error evaluating schedule '{schedule.name}': {e}")
            
            if not triggered_any:
                self.stdout.write("No active schedules are currently due.")
            return

        sync_type = options.get('type', 'both')
        if sync_type not in ('students', 'teachers', 'both'):
            self.stderr.write(f"Invalid sync type: {sync_type}")
            return

        # Create a pending SyncJob with specified type
        job = SyncJob.objects.create(status='Pending', sync_type=sync_type)
        self.stdout.write(f"Created sync job #{job.id} in 'Pending' state with type '{sync_type}'.")
        
        # Execute the sync job helper synchronously
        run_sync_job_background(job.id)
        
        # Reload the job from the database to see the final status
        job.refresh_from_db()
        self.stdout.write(f"Sync job #{job.id} execution completed. Final Status: {job.status}")
