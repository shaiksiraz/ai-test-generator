import { Page, Locator, expect } from '@playwright/test';

export class SearchBddPage {
  readonly page: Page;
  readonly searchButton: Locator;
  readonly searchInput: Locator;
  readonly searchResult: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchButton = page.locator('button.DocSearch-Button');
    this.searchInput = page.locator('input.DocSearch-Input'); // Corrected locator
    this.searchResult = page.locator('.DocSearch-Hit');
  }

  async navigateTo(url: string): Promise<void> {
    await this.page.goto(url);
    await expect(this.page).toHaveURL(url);
  }

  async openSearchModal(): Promise<void> {
    await this.searchButton.click();
    await expect(this.searchInput).toBeVisible(); // Ensure the input is visible after clicking the search button
  }

  async searchFor(query: string): Promise<void> {
    await this.searchInput.type(query, { delay: 100 }); // Simulate human-like typing
    await expect(this.searchResult.first()).toBeVisible(); // Wait for the first search result to be visible
    await this.page.keyboard.press('Enter'); // Press Enter to confirm the search
  }

  async verifyUrlContains(text: string): Promise<void> {
    await expect(this.page).toHaveURL(new RegExp(text)); // Verify the URL contains the expected text
  }
}