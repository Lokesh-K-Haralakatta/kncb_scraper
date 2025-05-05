# token_manager.py
from playwright.sync_api import sync_playwright

class TokenManager:
    """
    Manages fetching and refreshing the X-IAS-API-REQUEST token via Playwright.
    """
    def __init__(self):
        self._token = None

    def fetch_token(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            token_holder = {}

            def handle_request(route, request):
                hdrs = request.headers
                if 'x-ias-api-request' in hdrs:
                    token_holder['token'] = hdrs['x-ias-api-request']
                route.continue_()

            page.route("**/*", handle_request)
            page.goto("https://matchcentre.kncb.nl/")
            page.wait_for_timeout(5000)
            browser.close()

        self._token = token_holder.get('token')
        if not self._token:
            raise RuntimeError("Failed to fetch X-IAS-API-REQUEST token")
        return self._token

    @property
    def token(self):
        if not self._token:
            return self.fetch_token()
        return self._token

    def refresh(self):
        """Force-fetch a new token."""
        return self.fetch_token()