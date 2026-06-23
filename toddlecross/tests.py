from unittest.mock import patch
# pyrefly: ignore [missing-import]
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User

@override_settings(
    TODDLE_LTI_ISSUER='https://ap-southeast-1-production-apis.toddleapp.com/394761314477637866',
    TODDLE_LTI_CLIENT_ID='9ad1aedfa10bcf126f0af53db4fbd156',
    TODDLE_LTI_LOGIN_URL='https://ap-southeast-1-production-apis.toddleapp.com/lti/oidc',
    TODDLE_LTI_KEYSET_URL='https://ap-southeast-1-production-apis.toddleapp.com/lti/jwks/394761314477637866',
    TODDLE_LTI_TOKEN_URL='https://ap-southeast-1-production-apis.toddleapp.com/lti/token',
    TODDLE_LTI_DEPLOYMENT_ID='d95e7df7'
)
class LtiViewsTests(TestCase):
    def setUp(self):
        # Create an existing test user
        self.existing_user = User.objects.create_user(
            username='existing_teacher',
            email='teacher@example.com',
            password='testpassword'
        )

    def test_lti_keyset_view(self):
        """Test that the JWKS endpoint returns the public key(s)."""
        response = self.client.get(reverse('toddlecross:lti_keyset'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('keys', data)
        self.assertTrue(len(data['keys']) > 0)
        self.assertEqual(data['keys'][0]['alg'], 'RS256')

    @patch('pylti1p3.contrib.django.DjangoOIDCLogin.redirect')
    def test_lti_login_view(self, mock_redirect):
        """Test that the OIDC login view initiates redirect properly."""
        from django.http import HttpResponseRedirect
        mock_redirect.return_value = HttpResponseRedirect('https://toddle.com/oidc')
        
        response = self.client.get(reverse('toddlecross:lti_login'), {
            'iss': 'https://ap-southeast-1-production-apis.toddleapp.com/394761314477637866',
            'login_hint': 'hint123',
            'client_id': '9ad1aedfa10bcf126f0af53db4fbd156'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://toddle.com/oidc')

    @patch('pylti1p3.contrib.django.DjangoMessageLaunch.get_launch_data')
    def test_lti_launch_success_existing_user(self, mock_get_launch_data):
        """Test successful LTI launch redirects to dashboard if user exists."""
        mock_get_launch_data.return_value = {
            'email': 'teacher@example.com',
            'sub': 'toddle-user-123',
            'name': 'Test Teacher'
        }
        
        response = self.client.post(reverse('toddlecross:lti_launch'))
        # Successful login redirects to '/'
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        
        # Check that user is logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), self.existing_user.pk)

    @patch('pylti1p3.contrib.django.DjangoMessageLaunch.get_launch_data')
    def test_lti_launch_fail_user_not_exist(self, mock_get_launch_data):
        """Test that LTI launch returns a 403 error page if user does not exist in Django."""
        mock_get_launch_data.return_value = {
            'email': 'nonexistent@example.com',
            'sub': 'toddle-user-999',
            'name': 'Stranger'
        }
        
        response = self.client.post(reverse('toddlecross:lti_launch'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'toddlecross/lti_error.html')
        self.assertContains(response, 'No account exists for nonexistent@example.com', status_code=403)
        
        # Check that user is NOT logged in
        self.assertNotIn('_auth_user_id', self.client.session)

    @patch('pylti1p3.contrib.django.DjangoMessageLaunch.get_launch_data')
    def test_lti_launch_fail_missing_email(self, mock_get_launch_data):
        """Test that LTI launch returns 403 if email claim is missing."""
        mock_get_launch_data.return_value = {
            'sub': 'toddle-user-999',
            'name': 'Stranger'
        }
        
        response = self.client.post(reverse('toddlecross:lti_launch'))
        self.assertEqual(response.status_code, 403)
        # Check that user is NOT logged in
        self.assertNotIn('_auth_user_id', self.client.session)


class AccessGatingTests(TestCase):
    def test_anonymous_access_home_allowed(self):
        """Unauthenticated user should be allowed to view the home/login page."""
        response = self.client.get(reverse('toddlecross:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'toddlecross/login.html')

    def test_anonymous_access_protected_redirects(self):
        """Unauthenticated user accessing admin or other views should redirect to LOGIN_URL (/)."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        # Verify it redirects to the login path /
        self.assertTrue(response.url.startswith('/'))

    def test_anonymous_access_allauth_login_allowed(self):
        """Unauthenticated user should be allowed to view allauth login/signup pages."""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)


class UserManagementTests(TestCase):
    def setUp(self):
        # We create a regular test user that is NOT a staff member.
        self.regular_user = User.objects.create_user(
            username='regular_user@example.com',
            email='regular_user@example.com',
            password='testpassword'
        )
        # We create a staff user who is an administrator.
        self.staff_user = User.objects.create_user(
            username='staff_user@example.com',
            email='staff_user@example.com',
            password='testpassword',
            is_staff=True
        )

    def test_regular_user_dashboard_does_not_list_users(self):
        # We log in as the regular user.
        self.client.force_login(self.regular_user)
        # We fetch the dashboard page.
        response = self.client.get(reverse('toddlecross:home'))
        # The page should load successfully (status code 200).
        self.assertEqual(response.status_code, 200)
        # We check that the context does NOT contain the list of users.
        self.assertNotIn('users', response.context)

    def test_staff_user_dashboard_lists_users(self):
        # We log in as the staff administrator.
        self.client.force_login(self.staff_user)
        # We fetch the dashboard page.
        response = self.client.get(reverse('toddlecross:home'))
        # The page should load successfully (status code 200).
        self.assertEqual(response.status_code, 200)
        # The context must contain our list of users.
        self.assertIn('users', response.context)
        # The list must contain the users we registered in setUp.
        user_list = response.context['users']
        self.assertTrue(any(u.email == 'regular_user@example.com' for u in user_list))

    def test_regular_user_cannot_invite_users(self):
        # We log in as the regular user.
        self.client.force_login(self.regular_user)
        # We attempt to POST to the invite URL.
        response = self.client.post(reverse('toddlecross:invite_user'), {
            'email': 'new_invitee@example.com'
        })
        # The system must stop them and return a 403 Forbidden status code.
        self.assertEqual(response.status_code, 403)
        # We check that the user was NOT created in the database.
        self.assertFalse(User.objects.filter(email='new_invitee@example.com').exists())

    def test_staff_user_can_invite_users(self):
        # We log in as the staff administrator.
        self.client.force_login(self.staff_user)
        # We post a new email address to the invite URL.
        response = self.client.post(reverse('toddlecross:invite_user'), {
            'email': 'new_invitee@example.com',
            'is_staff': 'off'
        })
        # The page should redirect us back to the homepage (status code 302).
        self.assertEqual(response.status_code, 302)
        # The new user must now exist in our database.
        self.assertTrue(User.objects.filter(email='new_invitee@example.com').exists())
        invited_user = User.objects.get(email='new_invitee@example.com')
        # They should NOT be a staff member.
        self.assertFalse(invited_user.is_staff)
        # Their password must be unusable since they will use SSO.
        self.assertFalse(invited_user.has_usable_password())

    def test_invite_duplicate_user_fails(self):
        # We log in as the staff administrator.
        self.client.force_login(self.staff_user)
        # We attempt to invite an email that already exists (regular_user).
        response = self.client.post(reverse('toddlecross:invite_user'), {
            'email': 'regular_user@example.com'
        })
        # It should redirect back to the home page.
        self.assertEqual(response.status_code, 302)
        # Only 1 user with that email should exist.
        self.assertEqual(User.objects.filter(email='regular_user@example.com').count(), 1)


