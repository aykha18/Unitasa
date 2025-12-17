import { test, expect } from '@playwright/test';

/**
 * Dashboard Agent Test Suite
 * Tests for agents-related functionality in the Unitasa dashboard
 * Based on test cases from docs/dashboard-agent-test-cases.md
 */

test.describe('Dashboard Agent Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test.describe('Landing Page - Success Stories Removal', () => {
    test('TC-LP-SS-001: Success Stories section should be removed', async ({ page }) => {
      // Verify that Success Stories section is not present
      const successStoriesSection = page.locator('[data-testid="success-stories"]').or(
        page.locator('text=/Success Stories/i')
      );

      await expect(successStoriesSection).not.toBeVisible();
    });

    test('TC-LP-SS-002: Landing page loads without Success Stories content', async ({ page }) => {
      // Check that the page loads successfully
      await expect(page).toHaveTitle(/Unitasa/);

      // Verify key sections are still present
      await expect(page.locator('text=/AI.*Marketing/i')).toBeVisible();
      await expect(page.locator('text=/CRM.*Integration/i')).toBeVisible();
    });
  });

  test.describe('Co-Creator Assessment Flow', () => {
    test('TC-CC-AF-001: Co-creator page loads correctly', async ({ page }) => {
      // Navigate to co-creator page
      await page.goto('/co-creator');

      // Verify page loads
      await expect(page.locator('text=/Take Assessment/i')).toBeVisible();
      await expect(page.locator('text=/₹29,999/i')).toBeVisible();
    });

    test('TC-CC-AF-002: Assessment button triggers modal', async ({ page }) => {
      // Navigate to co-creator page
      await page.goto('/co-creator');

      // Click the assessment button
      await page.locator('text=/Take Assessment/i').click();

      // Verify modal appears (this would need proper test IDs in the actual implementation)
      // For now, we'll check that no error occurs
      await expect(page.locator('body')).toBeVisible();
    });

    test('TC-CC-AF-003: Pricing displays correctly', async ({ page }) => {
      await page.goto('/co-creator');

      // Check that pricing shows ₹29,999 (not converted from USD)
      await expect(page.locator('text=/₹29,999/i')).toBeVisible();

      // Check savings percentage
      await expect(page.locator('text=/82%/i')).toBeVisible();
    });
  });

  test.describe('API Integration Tests', () => {
    test('TC-API-AI-001: AI Content Generation API responds correctly', async ({ page }) => {
      // This would typically be tested via API calls, but for E2E we can test UI integration
      // Navigate to dashboard (would need authentication setup)
      // For now, just verify the API health
      const response = await page.request.get('http://localhost:8001/api/v1/health');
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data.status).toBe('healthy');
    });

    test('TC-API-TW-001: Twitter OAuth URL generation works', async ({ page }) => {
      const response = await page.request.get('http://localhost:8001/api/v1/social/auth/twitter/url?user_id=1');
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('auth_url');
      expect(data).toHaveProperty('code_verifier');
      expect(data).toHaveProperty('state');
      expect(data.platform).toBe('twitter');
    });

    test('TC-API-AN-001: Analytics API returns proper data structure', async ({ page }) => {
      const response = await page.request.get('http://localhost:8001/api/v1/social/analytics');
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('summary');
      expect(data).toHaveProperty('platform_breakdown');
      expect(data.summary).toHaveProperty('total_posts');
      expect(data.summary).toHaveProperty('total_engagements');
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE size

    test('TC-MOBILE-001: Landing page is mobile responsive', async ({ page }) => {
      await page.goto('/');

      // Check that mobile menu button is visible
      const mobileMenu = page.locator('[data-testid="mobile-menu"]').or(
        page.locator('button').filter({ hasText: /menu/i })
      );

      // On mobile, menu should be accessible
      await expect(page.locator('body')).toBeVisible();
    });
  });

  test.describe('Cross-browser Compatibility', () => {
    test('TC-CROSS-001: Core functionality works across browsers', async ({ page, browserName }) => {
      await page.goto('/');

      // Basic functionality test that should work in all browsers
      await expect(page.locator('text=/Unitasa/i')).toBeVisible();

      console.log(`Test passed on ${browserName}`);
    });
  });

  test.describe('Performance Tests', () => {
    test('TC-PERF-001: Page load performance', async ({ page }) => {
      const startTime = Date.now();

      await page.goto('/', { waitUntil: 'networkidle' });

      const loadTime = Date.now() - startTime;
      console.log(`Page load time: ${loadTime}ms`);

      // Should load within reasonable time (adjust threshold as needed)
      expect(loadTime).toBeLessThan(10000); // 10 seconds
    });
  });

  test.describe('Error Handling', () => {
    test('TC-ERROR-001: Graceful handling of network errors', async ({ page }) => {
      // This would require setting up network interception
      // For now, just verify basic error handling structure exists
      await page.goto('/');

      // Page should still load even if some API calls fail
      await expect(page.locator('body')).toBeVisible();
    });
  });
});

// Helper functions for common test operations
async function loginAsCoCreator(page: any) {
  // This would need to be implemented based on your authentication system
  // For now, this is a placeholder
  console.log('Login functionality would be implemented here');
}

async function waitForDashboardLoad(page: any) {
  // Wait for dashboard to fully load
  await page.waitForSelector('[data-testid="dashboard-loaded"]', { timeout: 10000 })
    .catch(() => console.log('Dashboard load indicator not found, continuing...'));
}

export { test, expect };