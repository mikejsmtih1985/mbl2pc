"""
End-to-end tests for the web application using Playwright.
"""

import re

from playwright.sync_api import Page, expect


def test_redirects_to_login_if_not_authenticated(page: Page, web_server, base_url):
    """
    Tests that accessing a protected page without being logged in
    redirects the user to the login page or Google's OAuth page.
    """
    page.goto(f"{base_url}/send.html")
    # The URL should change to either contain '/login' or a google.com domain for OAuth
    expect(page).to_have_url(re.compile(r"/login|google\.com"))


def test_static_send_html_is_accessible(page: Page, web_server, base_url):
    """
    Tests that the raw static HTML file is served correctly.
    Note: This tests direct access. The main /send.html route should protect it.
    """
    response = page.goto(f"{base_url}/static/send.html")
    assert response.status == 200


def test_api_returns_401_for_unauthenticated_access(page: Page, web_server, base_url):
    """
    Tests that the API endpoints are protected and return a 401 Unauthorized
    status code when accessed without a valid session.
    """
    with page.expect_response("**/messages") as response_info:
        page.goto(f"{base_url}/messages")

    response = response_info.value
    assert response.status == 401
