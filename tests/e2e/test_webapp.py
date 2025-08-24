"""
End-to-end tests for the web application using Playwright.
"""

from playwright.sync_api import Page, expect


def test_redirects_to_login_if_not_authenticated(page: Page, web_server, base_url):
    """
    Tests that accessing the root URL redirects to the login page
    when the user is not authenticated.
    """
    page.goto(base_url)
    expect(page).to_have_url(f"{base_url}/login")


def test_static_send_html_is_accessible(page: Page, web_server, base_url):
    """
    Tests that the static/send.html page is accessible without authentication.
    """
    page.goto(f"{base_url}/send.html")
    expect(page).to_have_title("Send a message")


def test_api_returns_401_for_unauthenticated_access(page: Page, web_server, base_url):
    """
    Tests that API endpoints return a 401 Unauthorized error when accessed
    without authentication.
    """
    api_routes = ["/messages", "/send", "/send-image"]
    for route in api_routes:
        response = page.request.get(f"{base_url}{route}")
        expect(response.status).to_be(401)
