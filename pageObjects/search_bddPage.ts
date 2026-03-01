import { Page, Locator, expect } from '@playwright/test';

export class SearchBddPage {
  readonly page: Page;
  readonly searchButton: Locator;
  readonly searchInput: Locator;
  readonly searchResult: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchButton = page.locator('button.DocSearch-Button');
    this.searchInput = page.locator('input.DocSearch-Input');
    this.searchResult = page.locator('.DocSearch-Hit');
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
    await expect(this.searchResult.first()).toBeVisible();
    await this.searchInput.press('Enter');
  }

  async verifyUrlContains(text: string): Promise<void> {
    await expect(this.page).toHaveURL(new RegExp(text));
  }
}