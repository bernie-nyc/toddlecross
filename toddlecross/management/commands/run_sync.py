from django.core.management.base import BaseCommand
from toddlecross.models import SyncJob
from toddlecross.views import run_sync_job_background

class Command(BaseCommand):
    help = 'Executes the data sync pipeline synchronously and records execution metrics.'

    def handle(self, *args, **options):
        # Create a pending SyncJob
        job = SyncJob.objects.create(status='Pending')
        self.stdout.write(f"Created sync job #{job.id} in 'Pending' state.")
        
        # Execute the sync job helper synchronously
        run_sync_job_background(job.id)
        
        # Reload the job from the database to see the final status
        job.refresh_from_db()
        self.stdout.write(f"Sync job #{job.id} execution completed. Final Status: {job.status}")
