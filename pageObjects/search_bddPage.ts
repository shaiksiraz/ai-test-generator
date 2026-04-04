import { Page, Locator, expect, test } from '@playwright/test';

export class SearchPage {
  private readonly page: Page;
  private readonly searchButton: Locator;
  private readonly searchInput: Locator;
  private readonly firstSearchResult: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchButton = page.locator('button.DocSearch-Button');
    this.searchInput = page.locator('input.DocSearch-Input');
    this.firstSearchResult = page.locator('.DocSearch-Hit').first();
  }

  async navigateTo(url: string): Promise<void> {
    await test.step(`Navigate to URL: ${url}`, async () => {
      await this.page.goto(url);
      await expect(this.page).toHaveURL(url);
    });
  }

  async openSearchModal(): Promise<void> {
    await test.step('Click the Search button to open the modal', async () => {
      await this.searchButton.click();
      await expect(this.searchInput).toBeVisible();
    });
  }

  async searchFor(query: string): Promise<void> {
    await test.step(`Fill the search input with '${query}'`, async () => {
      await this.searchInput.pressSequentially(query, { delay: 100 });
      await expect(this.firstSearchResult).toBeVisible();
    });
  }

  async selectFirstSearchResult(): Promise<void> {
    await test.step('Select the first result from the search dropdown', async () => {
      await this.firstSearchResult.click();
    });
  }

  async verifyUrlContains(expectedText: string): Promise<void> {
    await test.step(`Verify the URL contains '${expectedText}'`, async () => {
      await expect(this.page).toHaveURL(new RegExp(expectedText));
    });
  }
}