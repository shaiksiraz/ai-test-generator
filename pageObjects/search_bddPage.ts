import { Page, Locator } from '@playwright/test';

export class SearchBDDPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly searchResults: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.locator('#search-input');
    this.searchButton = page.locator('#search-button');
    this.searchResults = page.locator('#search-results');
  }

  async enterSearchTerm(term: string): Promise<void> {
    await this.searchInput.fill(term);
  }

  async clickSearchButton(): Promise<void> {
    await this.searchButton.click();
  }

  async getSearchResults(): Promise<string[]> {
    return await this.searchResults.allTextContents();
  }
}