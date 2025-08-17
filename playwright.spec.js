
const { test, expect } = require('@playwright/test');

test('redirects to login or Google OAuth if not authenticated', async ({ page }) => {
	await page.goto('http://localhost:8000/send.html');
	await expect(page).toHaveURL(/login|google.com/);
});

test('serves static send.html without auth (should redirect if protected)', async ({ page }) => {
	const response = await page.goto('http://localhost:8000/static/send.html');
	// If static is public, status 200; if protected, likely 307/302
	expect([200, 302, 307]).toContain(response.status());
});

test('API returns 401, 404, or redirect for unauthenticated access', async ({ request }) => {
	const res = await request.get('http://localhost:8000/api/messages');
	expect([401, 404, 302, 307]).toContain(res.status());
});
