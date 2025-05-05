from playwright.sync_api import sync_playwright

def get_ias_token():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Change to True for silent run
        page = browser.new_page()
        token_holder = {}

        def handle_request(route, request):
            headers = request.headers
            if 'x-ias-api-request' in headers:
                token_holder['token'] = headers['x-ias-api-request']
                print(f"Captured X-IAS-API-REQUEST: {token_holder['token']}")
            route.continue_()

        # Intercept requests to capture header
        page.route("**/*", handle_request)

        # Navigate to the page
        page.goto("https://matchcentre.kncb.nl/")
        page.wait_for_timeout(5000)  # Wait 5 seconds to ensure network requests load

        browser.close()
        return token_holder.get("token")

# Run it
if __name__ == "__main__":
    token = get_ias_token()
    print(f"\n✅ Extracted Token: {token}")
