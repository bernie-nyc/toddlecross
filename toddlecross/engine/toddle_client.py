import requests
from django.conf import settings

# This class handles connecting to the Toddleapp API.
# It allows us to retrieve data and update records.
class ToddleClient:
    # This initializer runs when we create a new ToddleClient object.
    def __init__(self):
        # We load the base URL from our Django settings.
        self.base_url = getattr(settings, 'TODDLE_API_BASE_URL', 'https://ap-southeast-1-production-apis.toddleapp.com/')
        # We load the API key from our Django settings.
        self.api_key = getattr(settings, 'TODDLE_API_KEY', '')

    # This method sends a GraphQL request to Toddle.
    # It takes a query string and an optional dictionary of variables.
    def execute_graphql(self, query, variables=None):
        # We build the full URL to the GraphQL endpoint.
        url = f"{self.base_url.rstrip('/')}/graphql"
        
        # We configure the request headers to include our authorization API key.
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # We pack our query and variables into a single dictionary payload.
        payload = {
            'query': query
        }
        if variables:
            payload['variables'] = variables
            
        # We send the POST request to the Toddle server.
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # We check if the response status code indicates success.
        # If it failed (like a 401 or 500 error), we raise an error.
        response.raise_for_status()
        
        # We parse the response as JSON and return the dictionary back.
        return response.json()

    # This method sends a standard REST GET request to Toddle.
    # It takes a path endpoint (for example: '/v1/users').
    def execute_rest_get(self, path, params=None):
        # We build the full URL by combining base URL and path.
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        # We configure headers to include our authorization API key.
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # We send the GET request to the Toddle server.
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        # We raise an error if the request was not successful.
        response.raise_for_status()
        
        # We parse the response as JSON and return it.
        return response.json()

    # This method sends a standard REST POST request to Toddle.
    # It takes a path endpoint and a dictionary payload.
    def execute_rest_post(self, path, data=None):
        # We build the full URL.
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        # We configure headers to include our authorization API key.
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # We send the POST request with the JSON data.
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # We raise an error if the request was not successful.
        response.raise_for_status()
        
        # We parse and return the JSON response.
        return response.json()
