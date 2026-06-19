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
