// @ts-check
const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:8000/send.html';
const API_KEY = 'LetMeINN85!';

test.describe('mbl2pc Chat UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    // Set sender and key in localStorage
    await page.evaluate((key) => {
      localStorage.setItem('mbl2pc_sender', 'playwright');
      localStorage.setItem('mbl2pc_key', key);
    }, API_KEY);
    await page.reload();
  });

  test('can send a text message', async ({ page }) => {
    await page.fill('#msg', 'Hello from Playwright!');
    await page.click('button[type=submit]');
    await expect(page.locator('#result')).toContainText(/Sent|received/i);
    await page.waitForTimeout(1000);
    await expect(page.locator('#chat')).toContainText('Hello from Playwright!');
  });

  test('shows error for empty image upload', async ({ page }) => {
    await page.click('#imgForm button[type=submit]');
    await expect(page.locator('#result')).toContainText('Please select an image file');
  });

  test('can upload an image file', async ({ page }) => {
    // Create a fake image file
    const filePath = 'test.png';
    const buffer = Buffer.from([137,80,78,71,13,10,26,10,0,0,0,13,73,72,68,82,0,0,0,1,0,0,0,1,8,6,0,0,0,31,21,196,137,0,0,0,12,73,68,65,84,8,153,99,0,1,0,0,5,0,1,13,10,26,10,0,0,0,0,73,69,78,68,174,66,96,130]);
    await page.setInputFiles('#imgInput', { name: filePath, mimeType: 'image/png', buffer });
    await page.click('#imgForm button[type=submit]');
    await expect(page.locator('#result')).toContainText(/Image sent|received/i);
    await page.waitForTimeout(1000);
    // Check that an <img> appears in chat
    await expect(page.locator('#chat img')).toHaveCount(1);
  });

  test('shows error for non-image drag-and-drop', async ({ page }) => {
    // Simulate dropping a text file using browser context
    await page.evaluate(() => {
      const dt = new DataTransfer();
      dt.items.add(new File(['notanimage'], 'test.txt', { type: 'text/plain' }));
      const event = new DragEvent('drop', { dataTransfer: dt });
      document.body.dispatchEvent(event);
    });
    await expect(page.locator('#result')).toContainText('Only image files are allowed');
  });
});
