import { Page, Locator, expect } from '@playwright/test';

export class SearchBDDPage {
  readonly page: Page;
  readonly searchButton: Locator;
  readonly searchInput: Locator;
  readonly firstSearchResult: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchButton = page.locator('button.DocSearch-Button');
    this.searchInput = page.locator('input.DocSearch-Input');
    this.firstSearchResult = page.locator('.DocSearch-Hit').first();
  }

  async navigateTo(url: string): Promise<void> {
    await this.page.goto(url);
    await expect(this.page).toHaveURL(url);
  }

  async openSearchModal(): Promise<void> {
    await this.searchButton.click();
    await expect(this.searchInput).toBeVisible();
  }

  async searchFor(query: string): Promise<void> {
    await this.searchInput.type(query, { delay: 100 });
    await expect(this.firstSearchResult).toBeVisible();
  }

  async selectFirstSearchResult(): Promise<void> {
    await this.firstSearchResult.click();
  }

  async verifyUrlContains(text: string): Promise<void> {
    await expect(this.page).toHaveURL(new RegExp(text));
  }
}