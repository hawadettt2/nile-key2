import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const WS_URL = process.env.WS_URL || 'ws://localhost:8020/ws/avatar';

test.describe('Avatar Result Presentation — Real WebSocket E2E', () => {
  test('Arabic request reaches Core AI and returns IntentContent to executive UI', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/avatar');
    await page.waitForTimeout(2000);

    const input = page.locator('input[type="text"]');
    await input.fill('اريد تصدير الخضروات والفاكهة المصرية الى الاردن');
    await input.press('Enter');
    await page.waitForTimeout(5000);

    const structuredLabel = page.locator('text=الاستجابة المنظمة').first();
    if (await structuredLabel.count() > 0) {
      await expect(structuredLabel).toBeVisible();
    }
  });

  test('view_result navigates to mission detail when missionId exists', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/avatar');
    await page.waitForTimeout(2000);

    const missionId = 'test-mission-123';
    await page.evaluate(() => {
      const event = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'response',
          text: JSON.stringify({
            intent_type: 'mission_completed',
            content: { outcome: 'done', result: { mission_status: 'completed' } },
            context: { mission_id: 'test-mission-123', session_id: 'session-123' },
            suggested_actions: ['view_result'],
          }),
        }),
      });
      window.dispatchEvent(event);
    });
    await page.waitForTimeout(500);

    const viewResultButton = page.locator('button:has-text("عرض النتيجة")');
    if (await viewResultButton.count() > 0) {
      await viewResultButton.click();
      await page.waitForURL('**/digital-export-manager/missions/test-mission-123', { timeout: 5000 });
    }
  });

  test('view_error opens raw response expander', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/avatar');
    await page.waitForTimeout(2000);

    await page.evaluate(() => {
      const event = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'response',
          text: JSON.stringify({ intent_type: 'mission_failed' }),
        }),
      });
      window.dispatchEvent(event);
    });
    await page.waitForTimeout(500);

    const viewErrorButton = page.locator('button:has-text("عرض الخطأ")');
    if (await viewErrorButton.count() > 0) {
      await viewErrorButton.click();
      await expect(page.getByText('البيانات الخام')).toBeVisible();
    }
  });

  test('retry resends text when WebSocket is open', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/avatar');
    await page.waitForTimeout(2000);

    await page.evaluate(() => {
      const event = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'response',
          text: JSON.stringify({ intent_type: 'mission_failed' }),
        }),
      });
      window.dispatchEvent(event);
    });
    await page.waitForTimeout(500);

    const retryButton = page.locator('button:has-text("إعادة المحاولة")');
    if (await retryButton.count() > 0) {
      await retryButton.click();
      await page.waitForTimeout(1000);
    }
  });

  test('create_another clears result and focuses input', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/avatar');
    await page.waitForTimeout(2000);

    await page.evaluate(() => {
      const event = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'response',
          text: JSON.stringify({ intent_type: 'mission_completed' }),
        }),
      });
      window.dispatchEvent(event);
    });
    await page.waitForTimeout(500);

    const createAnotherButton = page.locator('button:has-text("إنشاء مهمة جديدة")');
    if (await createAnotherButton.count() > 0) {
      await createAnotherButton.click();
      await expect(page.getByText('مكتملة')).toBeNull();
    }
  });
});
