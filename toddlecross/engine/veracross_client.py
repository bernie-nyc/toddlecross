import time
import requests
from django.conf import settings

# This class handles connecting to the Veracross API.
# It uses OAuth2 authentication to request datasets securely.
class VeracrossClient:
    # This initializer runs when we create a new VeracrossClient object.
    def __init__(self):
        # We load our credentials and base URLs from our Django settings.
        self.base_url = getattr(settings, 'VERACROSS_API_BASE_URL', '')
        self.token_url = getattr(settings, 'VERACROSS_TOKEN_URL', '')
        self.client_id = getattr(settings, 'VERACROSS_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'VERACROSS_CLIENT_SECRET', '')
        
        # We cache the token in memory so we do not make a token request on every API call.
        self._access_token = None
        # We store the time when the cached token will expire.
        self._token_expiry = 0.0

    # This helper method gets a valid access token.
    # If the token is missing or expired, it requests a new one.
    def get_access_token(self):
        # We check if we already have a token and it is still valid.
        # We subtract 60 seconds as a safety buffer.
        if self._access_token and time.time() < self._token_expiry - 60:
            return self._access_token
            
        # If we need a new token, we prepare the post parameters.
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        # We send a POST request to get the authorization token.
        response = requests.post(self.token_url, data=payload, timeout=30)
        
        # We raise an error if the request failed.
        response.raise_for_status()
        
        # We parse the response and save the token.
        data = response.json()
        self._access_token = data.get('access_token')
        
        # We extract how many seconds this token is valid. Default is 3600.
        expires_in = data.get('expires_in', 3600)
        
        # We calculate the exact time in seconds when this token will expire.
        self._token_expiry = time.time() + float(expires_in)
        
        return self._access_token

    # This method performs a GET request to Veracross.
    # It handles fetching the token and applying it to headers.
    def execute_get(self, path, params=None):
        # We retrieve our active token.
        token = self.get_access_token()
        
        # We build the complete endpoint URL.
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        # We set the headers to use the Bearer token authorization.
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        # We send the GET request.
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        # We check for errors and raise an exception if it failed.
        response.raise_for_status()
        
        # We parse and return the JSON payload.
        return response.json()

    # This method requests the student dataset from Veracross.
    def get_students(self, params=None):
        # We request the 'students' endpoint and return the list.
        return self.execute_get('students', params=params)

    # This method requests the teacher dataset from Veracross.
    def get_teachers(self, params=None):
        # We request the 'teachers' endpoint and return the list.
        return self.execute_get('teachers', params=params)
