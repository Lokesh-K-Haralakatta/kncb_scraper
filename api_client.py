# my_api_client.py
import requests

class MyApiClient:
    def __init__(self, token):
        self.base_url = "https://api.resultsvault.co.uk/rv/134453/"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "X-IAS-API-REQUEST": token,
            "Accept": "application/json",
            "Referer": "https://matchcentre.kncb.nl/",
            "Origin": "https://matchcentre.kncb.nl/",
        }
    
    def fetch(self, endpoint, params=None):
        """Fetches data from a specific endpoint, with optional query parameters."""
        full_url = self.base_url + endpoint.lstrip('/')  # Safely join base and endpoint
        response = requests.get(full_url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()