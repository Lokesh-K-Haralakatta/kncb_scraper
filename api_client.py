# api_client.py
import requests
from token_manager import TokenManager

class MyApiClient:
    """
    API client for ResultsVault-backed KNCB Match Centre.
    Automatically handles X-IAS-API-REQUEST token refresh on 401 errors.
    """
    BASE_URL = "https://api.resultsvault.co.uk/rv/134453/"
    MAX_FETCH_RETRIES = 1  # retry once after refreshing token

    def __init__(self, token=None):
        # Initialize token manager and prime the token
        self.token_manager = TokenManager()
        # If a manual token is passed, override the fetched one
        if token:
            self.token_manager._token = token
        # Fetch initial token
        self.token = self.token_manager.token
        self.base_url = self.BASE_URL

    def _get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "X-IAS-API-REQUEST": self.token,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en;q=0.7,nl;q=0.3",
            "Referer": "https://matchcentre.kncb.nl/",
            "Origin": "https://matchcentre.kncb.nl/",
            "DNT": "1",
            "Connection": "keep-alive",
        }

    def fetch(self, endpoint, params=None):
        """
        Fetches data from a specific endpoint, automatically refreshing the token on a 401.
        """
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        last_exc = None

        for attempt in range(self.MAX_FETCH_RETRIES + 1):
            headers = self._get_headers()
            response = requests.get(url, headers=headers, params=params)

            # If unauthorized on first attempt, refresh token and retry
            if response.status_code == 401 and attempt < self.MAX_FETCH_RETRIES:
                print("🔄 401 Unauthorized — refreshing token and retrying")
                self.token = self.token_manager.refresh()
                continue

            try:
                response.raise_for_status()
                return response.json()
            except requests.HTTPError as e:
                last_exc = e
                # For non-401 or after retry exhausted, break
                break

        # If we exit loop without return, raise last exception
        raise last_exc

    def fetch_scorecard(self, match_id):
        """
        Fetch full match scorecard (rich nested data).
        """
        endpoint = f"matches/{match_id}/"
        params = {
            'apiid': '1002',
            'strmflg': '3',
        }
        return self.fetch(endpoint, params)