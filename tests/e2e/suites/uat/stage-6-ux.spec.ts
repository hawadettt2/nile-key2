import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:8000';

async function createTestUser(page: any) {
  const username = `ov_ui_${Date.now().toString(36)}`;
  const response = await page.request.post(`${API_URL}/api/v1/auth/register`, {
    data: {
      email: `${username}@example.com`,
      username,
      full_name: `OV UI User`,
      password: 'TestPassword123!',
      role: 'owner',
      phone: '+201000000000',
      company: 'OV Test Co',
    },
  });
  expect(response.ok()).toBeTruthy();
  return { username, password: 'TestPassword123!' };
}

test.describe('OV-001 Stage 6.1 — Desktop Responsive 1920x1080', () => {
  test('Layout is responsive and sidebar is visible on desktop 1920x1080', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });

    await page.goto('/login');
    await expect(page).toHaveURL(/.*login/);

    const credentials = await createTestUser(page);

    await page.locator('input[type="text"]').fill(credentials.username);
    await page.locator('input[type="password"]').fill(credentials.password);
    await page.getByRole('button', { name: /sign in|login/i }).click();

    await page.waitForURL('**/', { timeout: 15000 });

    const sidebar = page.locator('aside, nav, [class*="sidebar"], [class*="Sidebar"], [data-testid="sidebar"]').first();
    await expect(sidebar).toBeVisible();

    const body = page.locator('body');
    const overflowX = await body.evaluate((el) => getComputedStyle(el).overflowX);
    expect(['visible', 'auto', 'scroll', 'clip']).toContain(overflowX.toLowerCase());

    await page.screenshot({ path: 'tests/e2e/evidence/stage6-1-desktop-1920x1080.png', fullPage: true });

    const mainContent = page.locator('main, [class*="main"], [class*="content"], [role="main"], .layout, [class*="layout"]').first();
    await expect(mainContent).toBeVisible();
  });
});
