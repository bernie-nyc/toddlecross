import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings

# This class defines a custom command that we can run using python manage.py.
# The name of the class must be Command, and it must inherit from BaseCommand.
class Command(BaseCommand):
    # This description helps users know what this command does when they list all commands.
    help = 'Ensures that a default superuser account exists in the database'

    # This method is the main entry point that runs when the command is called.
    def handle(self, *args, **options):
        # We fetch the username we want to use from our website configuration.
        username = getattr(settings, 'SUPERUSER_USERNAME', 'admin')
        # We fetch the email we want to use from our website configuration.
        email = getattr(settings, 'SUPERUSER_EMAIL', 'admin@example.com')
        # We fetch the password we want to use from our website configuration.
        password = getattr(settings, 'SUPERUSER_PASSWORD', 'adminpassword')

        # We search the database to check if a user with this username already exists.
        if User.objects.filter(username=username).exists():
            # If the user exists, we print a message to the console and stop.
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" already exists.'))
            return

        # If the user does not exist, we notify the administrator that we are creating it.
        self.stdout.write(f'Creating superuser account: {username} ({email})...')
        
        try:
            # We call the database function to create a new superuser account.
            # A superuser has all permissions to view, add, change, and delete database records.
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            # We print a success message to confirm that the user was created.
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}".'))
        except Exception as e:
            # If an error happens (for example, database is locked), we print the error message.
            self.stderr.write(self.style.ERROR(f'Failed to create superuser: {e}'))
