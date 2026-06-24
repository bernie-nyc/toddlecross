from unittest.mock import patch, MagicMock
# pyrefly: ignore [missing-import]
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User

from toddlecross.engine.toddle_client import ToddleClient
from toddlecross.engine.veracross_client import VeracrossClient
from toddlecross.engine.sync_pipeline import SyncPipeline

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


class ToddleClientTests(TestCase):
    @patch('requests.post')
    def test_execute_graphql_sends_correct_headers_and_payload(self, mock_post):
        # We mock the post request response to return a simple JSON dictionary.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'students': []}}
        mock_post.return_value = mock_response

        # We create our client object.
        client = ToddleClient()
        # We call execute_graphql.
        result = client.execute_graphql('query { test }', {'var': 123})

        # We verify it returned the correct parsed data.
        self.assertEqual(result, {'data': {'students': []}})
        # We check that requests.post was called with correct arguments.
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        # The first argument is the URL.
        self.assertTrue(args[0].endswith('/graphql'))
        # The json payload should contain our query and variables.
        self.assertEqual(kwargs['json'], {'query': 'query { test }', 'variables': {'var': 123}})
        # The headers should have our Content-Type and Authorization.
        self.assertEqual(kwargs['headers']['Content-Type'], 'application/json')
        self.assertIn('Authorization', kwargs['headers'])


class VeracrossClientTests(TestCase):
    @patch('requests.post')
    @patch('requests.get')
    def test_veracross_client_auth_and_get(self, mock_get, mock_post):
        # We mock the authentication response.
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {'access_token': 'fake_token', 'expires_in': 3600}
        mock_post.return_value = mock_auth_response

        # We mock the GET data response.
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{'id': 1, 'first_name': 'John'}]
        mock_get.return_value = mock_get_response

        # We configure our client.
        client = VeracrossClient()
        # We fetch the students.
        students = client.get_students()

        # Check results and calls.
        self.assertEqual(students, [{'id': 1, 'first_name': 'John'}])
        mock_post.assert_called_once()
        mock_get.assert_called_once()
        
        # Check that authorization header was used on GET request.
        _, get_kwargs = mock_get.call_args
        self.assertEqual(get_kwargs['headers']['Authorization'], 'Bearer fake_token')


class SyncPipelineTests(TestCase):
    def setUp(self):
        self.pipeline = SyncPipeline()

    def test_map_student_translates_fields(self):
        raw_student = {
            'student_id': 1001,
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'ALICE@example.com ',
            'grade_level': 'Grade 9'
        }
        mapped = self.pipeline.map_student(raw_student)
        self.assertEqual(mapped, {
            'sis_id': '1001',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'grade': 'Grade 9'
        })

    def test_calculate_diff_finds_correct_ops(self):
        existing = [
            {'email': 'keep@example.com', 'first_name': 'Keep', 'grade': 'G1'},
            {'email': 'update@example.com', 'first_name': 'OldName', 'grade': 'G1'},
            {'email': 'delete@example.com', 'first_name': 'Delete', 'grade': 'G2'}
        ]
        incoming = [
            {'email': 'keep@example.com', 'first_name': 'Keep', 'grade': 'G1'},
            {'email': 'update@example.com', 'first_name': 'NewName', 'grade': 'G1'},
            {'email': 'create@example.com', 'first_name': 'Create', 'grade': 'G3'}
        ]
        diff = self.pipeline.calculate_diff(existing, incoming)
        
        # We check the creations.
        self.assertEqual(len(diff['to_create']), 1)
        self.assertEqual(diff['to_create'][0]['email'], 'create@example.com')
        
        # We check the updates.
        self.assertEqual(len(diff['to_update']), 1)
        self.assertEqual(diff['to_update'][0]['first_name'], 'NewName')
        
        # We check the deletions.
        self.assertEqual(len(diff['to_delete']), 1)
        self.assertEqual(diff['to_delete'][0]['email'], 'delete@example.com')

    @patch.object(VeracrossClient, 'get_students')
    @patch.object(ToddleClient, 'execute_graphql')
    def test_sync_students_workflow(self, mock_graphql, mock_veracross_students):
        # We mock Veracross returning one new student.
        mock_veracross_students.return_value = [
            {'student_id': 999, 'first_name': 'Bob', 'last_name': 'Jones', 'email': 'bob@example.com', 'grade_level': 'G5'}
        ]
        
        # We mock Toddle graphql query returning empty list first, then successful mutation responses.
        mock_graphql.side_effect = [
            {'data': {'students': []}}, # GetExistingStudents response
            {'data': {'createStudent': {'sis_id': '999'}}} # CreateStudent response
        ]
        
        results = self.pipeline.sync_students()
        self.assertEqual(results['created_count'], 1)
        self.assertEqual(results['updated_count'], 0)
        self.assertEqual(results['deleted_count'], 0)


class SyncJobTests(TestCase):
    def setUp(self):
        # We create a regular test user that is NOT staff.
        self.regular_user = User.objects.create_user(
            username='regular_user@example.com',
            email='regular_user@example.com',
            password='testpassword'
        )
        # We create a staff administrator.
        self.staff_user = User.objects.create_user(
            username='staff_user@example.com',
            email='staff_user@example.com',
            password='testpassword',
            is_staff=True
        )

    def test_sync_job_add_log_helper(self):
        # We create a pending job.
        job = SyncJob.objects.create(status='Pending')
        job.add_log("First line")
        job.add_log("Second line")
        
        # Fetch it back from the database.
        db_job = SyncJob.objects.get(id=job.id)
        # Check logs field contents.
        self.assertEqual(db_job.logs, "First line\nSecond line\n")

    def test_regular_user_cannot_trigger_sync(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(reverse('toddlecross:trigger_sync'))
        # Should return 403 Forbidden.
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SyncJob.objects.count(), 0)

    @patch('threading.Thread')
    def test_staff_user_can_trigger_sync(self, mock_thread):
        self.client.force_login(self.staff_user)
        response = self.client.post(reverse('toddlecross:trigger_sync'))
        # Should return 200 OK with success JSON.
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('job_id', data)
        
        # Verify a background thread was started.
        mock_thread.assert_called_once()
        # Verify a SyncJob was created in Pending state.
        self.assertEqual(SyncJob.objects.count(), 1)
        job = SyncJob.objects.first()
        self.assertEqual(job.status, 'Pending')

    def test_sync_status_view_permissions(self):
        job = SyncJob.objects.create(status='Pending')
        
        # Regular user should be forbidden.
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('toddlecross:sync_status', args=[job.id]))
        self.assertEqual(response.status_code, 403)
        
        # Staff user should get successful JSON status.
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('toddlecross:sync_status', args=[job.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'Pending')
        self.assertEqual(data['id'], job.id)

    @patch.object(SyncPipeline, 'sync_students')
    def test_run_sync_job_background_success(self, mock_sync):
        job = SyncJob.objects.create(status='Pending')
        
        # Run the background helper synchronously in our test.
        run_sync_job_background(job.id)
        
        db_job = SyncJob.objects.get(id=job.id)
        # Should have updated status to Success.
        self.assertEqual(db_job.status, 'Success')
        self.assertIn("Complete database synchronization success", db_job.logs)
        self.assertIsNotNone(db_job.end_time)

    @patch.object(SyncPipeline, 'sync_students')
    def test_run_sync_job_background_failure(self, mock_sync):
        # We simulate a sync crash.
        mock_sync.side_effect = Exception("API connection lost")
        job = SyncJob.objects.create(status='Pending')
        
        run_sync_job_background(job.id)
        
        db_job = SyncJob.objects.get(id=job.id)
        # Should have updated status to Failed.
        self.assertEqual(db_job.status, 'Failed')
        self.assertIn("Process stopped due to error: API connection lost", db_job.logs)
        self.assertIsNotNone(db_job.end_time)




