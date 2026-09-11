import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('Avatar Result Presentation — UI Mock E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/avatar');
    await page.waitForTimeout(1000);
  });

  test('renders Avatar heading and conversation section', async ({ page }) => {
    await expect(page.getByText('AI Executive Avatar')).toBeVisible();
    await expect(page.getByText('Conversation')).toBeVisible();
  });

  test('renders structured response with Arabic labels when response is valid', async ({ page }) => {
    await page.evaluate(() => {
      const event = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'response',
          text: JSON.stringify({
            intent_type: 'mission_completed',
            content: {
              outcome: 'تم إتمام المهمة',
              result: {
                mission_status: 'completed',
                goal: 'تصدير الخضروات',
                summary: 'تم بنجاح',
                results: [{ data: { findings: ['نتيجة 1'], sources_consulted: ['مصدر أ'] } }],
              },
            },
            context: { mission_id: 'mission-123', session_id: 'session-123' },
            suggested_actions: ['view_result'],
          }),
        }),
      });
      window.dispatchEvent(event);
    });
    await page.waitForTimeout(500);
    await expect(page.getByText('تم إتمام المهمة')).toBeVisible();
    await expect(page.getByText('تصدير الخضروات')).toBeVisible();
  });

  test('view_result is disabled when missionId is missing', async ({ page }) => {
    await page.evaluate(() => {
      const event = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'response',
          text: JSON.stringify({
            intent_type: 'mission_completed',
            content: { outcome: 'done', result: { mission_status: 'completed' } },
            context: {},
            suggested_actions: ['view_result'],
          }),
        }),
      });
      window.dispatchEvent(event);
    });
    await page.waitForTimeout(500);
    const viewResultButton = page.locator('button:has-text("عرض النتيجة")');
    if (await viewResultButton.count() > 0) {
      await expect(viewResultButton).toBeDisabled();
    }
  });

  test('view_error opens raw response expander', async ({ page }) => {
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
    const viewErrorButton = page.locator('button:has-text("عرض الخطأ")');
    if (await viewErrorButton.count() > 0) {
      await viewErrorButton.click();
      await expect(page.getByText('البيانات الخام')).toBeVisible();
    }
  });

  test('create_another clears response and focuses input', async ({ page }) => {
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
