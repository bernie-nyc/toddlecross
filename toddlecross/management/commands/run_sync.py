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

    def handle(self, *args, **options):
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
