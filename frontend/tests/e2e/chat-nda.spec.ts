import { expect, test, type Route } from "@playwright/test";

const TITLE = `Playwright Chat NDA ${Date.now()}`;

async function fillRemainingFieldsManually(page: import("@playwright/test").Page) {
  // The chat fixture pre-fills title, governingLaw, and party0.company.
  // The user fills the rest by hand.
  await page.locator('textarea[name="purpose"]').fill("Evaluate a partnership.");
  await page.locator('input[name="effectiveDate"]').fill("2026-05-06");
  await page.locator('input[name="jurisdiction"]').fill("New Castle, DE");

  for (const partyIndex of [0, 1]) {
    await page
      .locator(`input[name="parties.${partyIndex}.printName"]`)
      .fill(partyIndex === 0 ? "Alice" : "Bob");
    await page
      .locator(`input[name="parties.${partyIndex}.title"]`)
      .fill(partyIndex === 0 ? "CEO" : "CTO");
    await page
      .locator(`input[name="parties.${partyIndex}.noticeAddress"]`)
      .fill(partyIndex === 0 ? "1 ACME Way" : "2 Globex Ave");
  }
  // Party 1 company is filled by the chat stub; only fill party 2.
  await page.locator('input[name="parties.1.company"]').fill("Globex LLC");
}

test.describe("Chat-driven NDA workflow", () => {
  test("AI extracts fields, user submits, document is created", async ({ page }) => {
    await page.route("**/chat", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          assistantMessage: "Got it. Anything else?",
          extractedValues: {
            title: TITLE,
            governingLaw: "Delaware",
            party1: { company: "ACME Inc." },
          },
        }),
      });
    });

    await page.goto("/new");
    await expect(page.getByRole("heading", { name: /AI Assistant/i })).toBeVisible();

    await page.getByLabel("Message").fill("Use Delaware law and call it " + TITLE);
    await page.getByRole("button", { name: /^Send$/ }).click();

    await expect(page.locator('input[name="title"]')).toHaveValue(TITLE);
    await expect(page.locator('input[name="governingLaw"]')).toHaveValue("Delaware");
    await expect(page.locator('input[name="parties.0.company"]')).toHaveValue("ACME Inc.");

    await fillRemainingFieldsManually(page);
    await page.getByRole("button", { name: /create document/i }).click();

    await expect(page).toHaveURL(/\/documents\/[\w-]+$/);
    await expect(page.getByRole("heading", { level: 1, name: TITLE })).toBeVisible();
  });

  test("AI unavailable shows banner and form remains usable", async ({ page }) => {
    await page.route("**/chat", async (route: Route) => {
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({ detail: "AI assistant is not configured." }),
      });
    });

    await page.goto("/new");
    await page.getByLabel("Message").fill("Hello");
    await page.getByRole("button", { name: /^Send$/ }).click();

    await expect(page.getByText(/AI assistant is unavailable/i)).toBeVisible();
    await expect(page.getByLabel("Message")).toBeDisabled();

    // Manual form path still works.
    await page.locator('input[name="title"]').fill("Manual " + TITLE);
    await page.locator('textarea[name="purpose"]').fill("Manual fill.");
    await page.locator('input[name="effectiveDate"]').fill("2026-05-06");
    await page.locator('input[name="governingLaw"]').fill("Delaware");
    await page.locator('input[name="jurisdiction"]').fill("New Castle, DE");
    for (const i of [0, 1]) {
      await page.locator(`input[name="parties.${i}.printName"]`).fill(i === 0 ? "A" : "B");
      await page.locator(`input[name="parties.${i}.title"]`).fill("CEO");
      await page.locator(`input[name="parties.${i}.company"]`).fill(i === 0 ? "X" : "Y");
      await page.locator(`input[name="parties.${i}.noticeAddress"]`).fill("1 Way");
    }
    await page.getByRole("button", { name: /create document/i }).click();
    await expect(page).toHaveURL(/\/documents\/[\w-]+$/);
  });
});
