from django.db import models

# This model stores the history and logs of each sync job run.
# It helps administrators monitor past executions and check for errors.
class SyncJob(models.Model):
    # The list of possible states a sync job can have.
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Running', 'Running'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]

    # The current state of this job (for example: Pending, Running, Success, or Failed).
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # The date and time when this job started running.
    start_time = models.DateTimeField(auto_now_add=True)

    # The date and time when this job finished running. Can be empty if it is still running.
    end_time = models.DateTimeField(null=True, blank=True)

    # A long text field containing details of what happened during the run.
    logs = models.TextField(default='', blank=True)

    # The number of new student records created during this run.
    created_count = models.IntegerField(default=0)

    # The number of student records updated during this run.
    updated_count = models.IntegerField(default=0)

    # The number of student records deleted/removed during this run.
    deleted_count = models.IntegerField(default=0)

    # This method appends a new message line to the logs and saves the model.
    def add_log(self, message):
        # We add the message followed by a newline character.
        self.logs = (self.logs or '') + str(message) + '\n'
        # We save the model immediately so the updates are available in real time.
        self.save()

    # This method defines how a SyncJob is printed as a string.
    def __str__(self):
        return f"Sync Job #{self.id} ({self.status})"
