from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, login_not_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden

# This view handles loading our homepage.
# We mark it with login_not_required so anyone can visit it without logging in first.
@login_not_required
def home_view(request):
    # If the visitor is already logged in, we show them the dashboard.
    if request.user.is_authenticated:
        context = {}
        # If the logged in user is a staff member (an administrator),
        # we fetch all registered users from the database so we can list them.
        # We sort them by the date they joined, newest first.
        if request.user.is_staff:
            context['users'] = User.objects.all().order_by('-date_joined')
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

