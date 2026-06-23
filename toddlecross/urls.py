from django.urls import path
from . import views
from . import lti_views

app_name = 'toddlecross'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('lti/login/', lti_views.lti_login, name='lti_login'),
    path('lti/launch/', lti_views.lti_launch, name='lti_launch'),
    path('lti/keyset/', lti_views.lti_keyset, name='lti_keyset'),
    # This path is where we send requests to invite/add new users.
    # It points to the invite_user_view function in our views.py file.
    path('invite-user/', views.invite_user_view, name='invite_user'),
]
