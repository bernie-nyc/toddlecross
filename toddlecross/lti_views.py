import os
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_not_required

from pylti1p3.tool_config import ToolConfDict
from pylti1p3.contrib.django import DjangoOIDCLogin, DjangoMessageLaunch, DjangoCacheDataStorage

def get_tool_conf():
    # Load keys
    try:
        with open(settings.LTI_PRIVATE_KEY_FILE, 'r') as f:
            private_key = f.read()
        with open(settings.LTI_PUBLIC_KEY_FILE, 'r') as f:
            public_key = f.read()
    except IOError as e:
        raise RuntimeError(f"LTI Key files not found: {e}")

    tool_conf = ToolConfDict({
        settings.TODDLE_LTI_ISSUER: [{
            "client_id": settings.TODDLE_LTI_CLIENT_ID,
            "auth_login_url": settings.TODDLE_LTI_LOGIN_URL,
            "auth_token_url": settings.TODDLE_LTI_TOKEN_URL,
            "key_set_url": settings.TODDLE_LTI_KEYSET_URL,
            "deployment_ids": [settings.TODDLE_LTI_DEPLOYMENT_ID]
        }]
    })
    tool_conf.set_private_key(settings.TODDLE_LTI_ISSUER, private_key, client_id=settings.TODDLE_LTI_CLIENT_ID)
    tool_conf.set_public_key(settings.TODDLE_LTI_ISSUER, public_key, client_id=settings.TODDLE_LTI_CLIENT_ID)
    return tool_conf

def get_launch_data_storage():
    return DjangoCacheDataStorage()

@login_not_required
def lti_login(request):
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()
    oidc_login = DjangoOIDCLogin(
        request, 
        tool_conf, 
        launch_data_storage=launch_data_storage
    )
    
    target_link_uri = request.GET.get('target_link_uri') or request.POST.get('target_link_uri')
    if not target_link_uri:
        target_link_uri = request.build_absolute_uri(reverse('toddlecross:lti_launch'))
        
    return oidc_login.enable_check_cookies().redirect(target_link_uri)

@csrf_exempt
@login_not_required
def lti_launch(request):
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()
    message_launch = DjangoMessageLaunch(
        request, 
        tool_conf, 
        launch_data_storage=launch_data_storage
    )
    
    try:
        launch_data = message_launch.get_launch_data()
    except Exception as e:
        return HttpResponseForbidden(f"LTI validation failed: {str(e)}")
        
    email = launch_data.get('email')
    if not email:
        custom_claims = launch_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {})
        email = custom_claims.get('email') or custom_claims.get('user_email')
        
    if not email:
        # Fallback to checking sub claim in case sub represents email (sometimes seen in LTI tests)
        sub = launch_data.get('sub')
        if sub and '@' in sub:
            email = sub

    if not email:
        return HttpResponseForbidden("LTI Launch error: Email claim is missing.")
        
    # Strict lookup: do not create user if they don't exist
    user = User.objects.filter(email=email).first()
    
    if not user:
        return render(request, 'toddlecross/lti_error.html', {
            'error_message': f"No account exists for {email} in Toddlecross. Please contact your administrator to register."
        }, status=403)
        
    # Log user in
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # Redirect to the dashboard
    return HttpResponseRedirect('/')

@login_not_required
def lti_keyset(request):
    tool_conf = get_tool_conf()
    jwks = tool_conf.get_jwks()
    return JsonResponse(jwks)
