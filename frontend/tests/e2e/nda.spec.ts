import { expect, test } from "@playwright/test";

const TITLE = `Playwright NDA ${Date.now()}`;

test.describe("NDA workflow", () => {
  test("create, view, persist across reload, and list", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("main").getByRole("link", { name: /new nda/i }).click();
    await expect(page).toHaveURL(/\/new$/);

    // Use input[name=...] selectors — labels like "Title" and "Date" appear in
    // multiple sections, but the underlying field names are unique.
    await page.locator('input[name="title"]').fill(TITLE);
    await page
      .locator('textarea[name="purpose"]')
      .fill("Evaluate a partnership.");
    await page.locator('input[name="effectiveDate"]').fill("2026-05-06");
    await page.locator('input[name="governingLaw"]').fill("Delaware");
    await page.locator('input[name="jurisdiction"]').fill("New Castle, DE");

    for (const partyIndex of [0, 1]) {
      await page
        .locator(`input[name="parties.${partyIndex}.printName"]`)
        .fill(partyIndex === 0 ? "Alice" : "Bob");
      await page
        .locator(`input[name="parties.${partyIndex}.title"]`)
        .fill(partyIndex === 0 ? "CEO" : "CTO");
      await page
        .locator(`input[name="parties.${partyIndex}.company"]`)
        .fill(partyIndex === 0 ? "ACME Inc." : "Globex LLC");
      await page
        .locator(`input[name="parties.${partyIndex}.noticeAddress"]`)
        .fill(partyIndex === 0 ? "1 ACME Way" : "2 Globex Ave");
    }

    await page.getByRole("button", { name: /create document/i }).click();

    await expect(page).toHaveURL(/\/documents\/[\w-]+$/);
    await expect(page.getByRole("heading", { level: 1, name: TITLE })).toBeVisible();
    await expect(page.getByText("Mutual Non-Disclosure Agreement").first()).toBeVisible();

    // Reload — persistence across browser refresh.
    await page.reload();
    await expect(page.getByRole("heading", { level: 1, name: TITLE })).toBeVisible();

    // Document appears on the home list.
    await page.goto("/");
    await expect(page.getByRole("link", { name: TITLE })).toBeVisible();
  });
});
