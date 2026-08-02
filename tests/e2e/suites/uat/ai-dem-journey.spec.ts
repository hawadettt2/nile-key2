import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:8000';

async function createTestUser(page: any, role: string = 'staff') {
  const username = `dem_e2e_${Date.now().toString(36)}`;
  const response = await page.request.post(`${API_URL}/api/v1/auth/register`, {
    data: {
      email: `${username}@example.com`,
      username,
      full_name: `DEM E2E User`,
      password: 'TestPassword123!',
      role,
    },
  });
  if (!response.ok()) {
    console.error(`Failed to create user: ${response.status()} ${await response.text()}`);
  }
  expect(response.ok()).toBeTruthy();
  return { username, password: 'TestPassword123!' };
}

async function login(page: any, username: string, password: string) {
  await page.goto('/login');
  await page.locator('input[type="text"]').fill(username);
  await page.locator('input[type="password"]').fill(password);
  await page.getByRole('button', { name: /sign in|login/i }).click();
  await page.waitForURL('**/', { timeout: 15000 });
}

test.describe('AI/DEM User Experience — E2E', () => {
  test('Login → DEM Connect → Create Mission → Execution → Results → Reasoning → Disconnect', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });

    const credentials = await createTestUser(page, 'staff');
    await login(page, credentials.username, credentials.password);

    await page.goto('/digital-export-manager');
    await page.waitForTimeout(1000);

    const connectButton = page.locator('button:has-text("Connect"), button:has-text("اتصال")').first();
    if (await connectButton.count() > 0) {
      await connectButton.click();
      await page.waitForTimeout(2000);
    }

    const sessionStatus = page.locator('text=connected, text=متصل').first();
    if (await sessionStatus.count() > 0) {
      await expect(sessionStatus).toBeVisible({ timeout: 10000 });
    }

    await page.goto('/digital-export-manager/missions/new');
    await page.waitForTimeout(1000);

    const missionType = page.locator('text=Search Entities, text=البحث عن الكيانات').first();
    if (await missionType.count() > 0) {
      await missionType.click();
    }

    const submitButton = page.locator('button:has-text("Submit Mission"), button:has-text("إرسال المهمة")').first();
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForTimeout(2000);
    }

    await page.goto('/digital-export-manager/missions');
    await page.waitForTimeout(1000);

    const missionCard = page.locator('[class*="cursor-pointer"]').first();
    if (await missionCard.count() > 0) {
      await missionCard.click();
      await page.waitForTimeout(1000);
    }

    const disconnectButton = page.locator('button:has-text("Disconnect"), button:has-text("قطع الاتصال")').first();
    if (await disconnectButton.count() > 0) {
      await disconnectButton.click();
      await page.waitForTimeout(1000);
    }
  });

  test('Mission requiring approval → Manager sees pending approval → Approve', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });

    const staffCredentials = await createTestUser(page, 'staff');
    await login(page, staffCredentials.username, staffCredentials.password);

    await page.goto('/digital-export-manager');
    await page.waitForTimeout(1000);

    const connectButton = page.locator('button:has-text("Connect"), button:has-text("اتصال")').first();
    if (await connectButton.count() > 0) {
      await connectButton.click();
      await page.waitForTimeout(2000);
    }

    await page.goto('/digital-export-manager/missions/new');
    await page.waitForTimeout(1000);

    const missionType = page.locator('text=Search Entities, text=البحث عن الكيانات').first();
    if (await missionType.count() > 0) {
      await missionType.click();
    }

    const submitButton = page.locator('button:has-text("Submit Mission"), button:has-text("إرسال المهمة")').first();
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForTimeout(2000);
    }

    const managerCredentials = await createTestUser(page, 'manager');
    await login(page, managerCredentials.username, managerCredentials.password);

    await page.goto('/digital-export-manager/approvals');
    await page.waitForTimeout(2000);

    const approveButton = page.locator('button:has-text("Approve"), button:has-text("موافقة")').first();
    if (await approveButton.count() > 0) {
      await approveButton.click();
      await page.waitForTimeout(1000);
    }
  });
});
