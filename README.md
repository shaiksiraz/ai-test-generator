# AI Test Generator (CLI Edition)

An AI-assisted test automation framework that auto-generates executable Playwright (TypeScript) tests from plain English CLI prompts. 

This framework utilizes a dual-stack micro-architecture, orchestrating AI calls with Python while executing the generated tests in a native Node.js/TypeScript Playwright environment.

## 🚀 Architecture & Features
* **Context-Injected Generation:** Silently navigates to the target URL, extracts the DOM, strips unnecessary bloat (scripts/styles/svgs), and feeds the clean HTML to the LLM to prevent locator hallucination.
* **LLM Agnostic:** Built on the OpenAI SDK standard, currently configured to use Groq's blazing-fast inference engine for instant test generation.
* **Auto-Execution:** Generates the `.spec.ts` file, sanitizes the markdown, and automatically triggers the Playwright test runner.

## 🛠️ Tech Stack
* **Orchestration:** Python 3.x, `openai` SDK, `beautifulsoup4`
* **Execution:** Node.js, TypeScript, Microsoft Playwright
* **AI Model:** Llama 3.3 70B (via Groq)

## ⚙️ Quick Start
1. Clone the repository.
2. Setup the Python Orchestrator:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   playwright install chromium

## 🎮 Usage
Pass your test steps directly via the CLI. Use the `--headed` flag to watch the execution.

```bash
python generate.py "Go to [https://playwright.dev](https://playwright.dev), click the Search button to open the modal, fill the search input with 'locators', press Enter, verify the url contains 'locators'" --name search_locators --run --headed