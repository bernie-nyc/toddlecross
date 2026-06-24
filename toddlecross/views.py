import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, login_not_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from .models import SyncJob
from .engine.sync_pipeline import SyncPipeline

# This background worker function runs the sync process inside a separate execution thread.
# Running in a thread allows our web server to respond instantly to the user while the work happens.
def run_sync_job_background(job_id):
    # We fetch the specific SyncJob record from the database.
    try:
        job = SyncJob.objects.get(id=job_id)
    except SyncJob.DoesNotExist:
        return

    # We update its status to Running.
    job.status = 'Running'
    job.save()

    job.add_log("Sync progress: Background worker thread started.")
    
    try:
        # We instantiate our mapping engine and pass the job object to handle logging.
        pipeline = SyncPipeline(sync_job=job)
        # We start the synchronization process for students.
        pipeline.sync_students()
        # If no error happened, we mark the job status as Success.
        job.status = 'Success'
        job.add_log("Sync progress: Complete database synchronization success.")
    except Exception as e:
        # If an error happens (like API timeout or incorrect keys), we record the failure.
        job.status = 'Failed'
        job.add_log(f"Sync error: Process stopped due to error: {e}")
    finally:
        # We record the exact end time and save our changes.
        job.end_time = timezone.now()
        job.save()

# This view handles loading our homepage.
# We mark it with login_not_required so anyone can visit it without logging in first.
@login_not_required
def home_view(request):
    # If the visitor is already logged in, we show them the dashboard.
    if request.user.is_authenticated:
        context = {}
        # If the logged in user is a staff member (an administrator),
        # we fetch all registered users and the 10 most recent sync job runs.
        if request.user.is_staff:
            context['users'] = User.objects.all().order_by('-date_joined')
            context['sync_jobs'] = SyncJob.objects.all().order_by('-start_time')[:10]
        # We render and send back the dashboard template with our list of users.
        return render(request, 'toddlecross/dashboard.html', context)
    
    # If they are not logged in, we show them the simple login page.
    return render(request, 'toddlecross/login.html')

# This view handles inviting or pre registering new users.
# Only logged in users can access this, so we use the login_required decorator.
@login_required
def invite_user_view(request):
    # We double check if the user is actually a staff member.
    # If they are not staff, we stop them and send a 403 Forbidden error page.
    if not request.user.is_staff:
        return HttpResponseForbidden("You must be an administrator to perform this action.")
    
    # We only process this action if the form was submitted using the POST method.
    if request.method == 'POST':
        # We extract the email address from the submitted form data and remove extra spaces.
        email = request.POST.get('email', '').strip()
        # We check if the is_staff checkbox was ticked in the form.
        is_staff_checked = request.POST.get('is_staff') == 'on'
        
        # If the administrator did not enter an email, we show an error message.
        if not email:
            messages.error(request, "Please enter a valid email address.")
            return redirect('toddlecross:home')
            
        # We check if a user with this email address is already registered in the database.
        if User.objects.filter(email=email).exists():
            # If the user exists, we show an error message and do not create a duplicate.
            messages.error(request, f"A user with email {email} is already registered.")
            return redirect('toddlecross:home')
            
        try:
            # We create a new user account in our database.
            # We set both the username and email to be the email address.
            # We also set their administrator status based on the checkbox.
            new_user = User.objects.create_user(
                username=email,
                email=email,
                is_staff=is_staff_checked
            )
            # Since the user will log in via Google SSO or LTI, they do not need a password.
            # We set their password to be unusable so they cannot log in using a password form.
            new_user.set_unusable_password()
            new_user.save()
            
            # We show a success message to the administrator.
            messages.success(request, f"Successfully invited/added user: {email}")
        except Exception as e:
            # If something goes wrong during creation, we show an error message with the details.
            messages.error(request, f"Failed to create user: {e}")
            
    # After processing, we redirect the administrator back to the homepage dashboard.
    return redirect('toddlecross:home')

# This view triggers a new background sync job.
@login_required
def trigger_sync_view(request):
    # Only administrators are allowed to run data sync jobs.
    if not request.user.is_staff:
        return HttpResponseForbidden("You must be an administrator to perform this action.")
        
    # We only accept POST requests to trigger execution.
    if request.method == 'POST':
        # We pre create the SyncJob database record to get a unique job ID.
        job = SyncJob.objects.create(status='Pending')
        job.add_log("Sync progress: Job initialized. Starting background thread...")
        
        # We start our background thread and specify run_sync_job_background as the target.
        thread = threading.Thread(target=run_sync_job_background, args=(job.id,))
        thread.daemon = True
        thread.start()
        
        # We immediately return the job ID to the frontend.
        return JsonResponse({'success': True, 'job_id': job.id})
        
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

# This view retrieves the status and logs of a running or completed sync job.
@login_required
def sync_status_view(request, job_id):
    # Only administrators are allowed to view sync status logs.
    if not request.user.is_staff:
        return HttpResponseForbidden("You must be an administrator to perform this action.")
        
    # We retrieve the specific SyncJob record or return a 404 error if it does not exist.
    job = get_object_or_404(SyncJob, id=job_id)
    
    # We package our data into a dictionary structure.
    data = {
        'id': job.id,
        'status': job.status,
        'logs': job.logs,
        'created_count': job.created_count,
        'updated_count': job.updated_count,
        'deleted_count': job.deleted_count,
        'start_time': job.start_time.isoformat() if job.start_time else None,
        'end_time': job.end_time.isoformat() if job.end_time else None,
    }
    
    # We return the data as a JSON response.
    return JsonResponse(data)


