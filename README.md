# AI Test Generator with Self-Healing & Docker

An AI-assisted test automation framework that **auto-generates and self-heals** executable Playwright (TypeScript) tests from plain English prompts or BDD feature files.

This framework utilizes a dual-stack architecture:
- **Python Orchestrator:** Handles AI test generation, DOM extraction, and intelligent test healing
- **TypeScript/Playwright Executor:** Runs the generated tests in a native Node.js environment

Supports both **local execution** and **containerized deployment** via Docker.

---

## ✨ Key Features

### 🧠 Intelligent Test Generation
- **Context-Injected Generation:** Automatically navigates to the target URL, extracts the clean DOM (removing scripts/styles/SVGs), and feeds it to the LLM to prevent locator hallucination
- **BDD Support:** Generate tests from Gherkin feature files (`.feature`)
- **LLM Agnostic:** Built on the OpenAI SDK standard, configured for Groq's Llama 3.3 70B with instant inference

### 🩹 Self-Healing Tests
- **Automatic Error Recovery:** Tests that fail are automatically analyzed and fixed by the AI
- **Configurable Retry Logic:** Set retry attempts for automatic healing attempts
- **Smart DOM Re-extraction:** Updates context on each healing iteration to reflect DOM changes

### 🐳 Docker Support
- **Containerized Execution:** Run tests in isolated Docker containers
- **Full Stack Included:** Dockerfile includes Node.js, Playwright browsers, and Python 3
- **Volume Mapping:** Generated files automatically sync to your local machine
- **Browser Pre-installed:** Playwright browsers are baked into the container

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Orchestration** | Python 3.x, OpenAI SDK, BeautifulSoup4 |
| **Execution** | Node.js, TypeScript, Microsoft Playwright |
| **Containerization** | Docker, Docker Compose |
| **AI Model** | Llama 3.3 70B (via Groq) |
| **Test Framework** | @playwright/test |

---

## 📋 Project Structure

```
.
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Multi-stage Docker build
├── generate.py                 # Main CLI entry point
├── package.json                # Node.js dependencies
├── requirements.txt            # Python dependencies
├── playwright.config.ts        # Playwright configuration
├── README.md                   # This file
│
├── src/
│   ├── test_generator.py       # Core test generation & healing logic
│   ├── llm_client.py           # LLM API communication
│   ├── dom_extractor.py        # DOM extraction & cleanup
│   └── __pycache__/
│
├── features/
│   └── *.feature              # BDD Gherkin feature files
│
├── pageObjects/
│   └── *.ts                   # TypeScript Page Object Models
│
├── prompts/
│   ├── coding_standards.txt   # AI coding guidelines
│   ├── generate_test.txt      # Test generation prompt
│   └── heal_test.txt          # Test healing prompt
│
├── tests/
│   └── generated/
│       └── *.spec.ts          # Auto-generated Playwright tests
│
└── playwright-report/         # Test execution reports
```

---

## ⚡ Quick Start

### Option 1: Local Setup (Windows/Mac/Linux)

#### Prerequisites
- Python 3.8+
- Node.js 16+
- Groq API Key (free tier available at [groq.com](https://console.groq.com))

#### Installation & Usage

1. **Clone & Setup Environment**
   ```bash
   git clone <repository-url>
   cd ai-test-generator
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   npx playwright install chromium
   ```

3. **Configure API Key**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run Test Generation with Auto-Healing**
   ```bash
   python generate.py "your test scenario here" --name test_name --run --headed
   ```

---

### Option 2: Docker Setup (Recommended)

#### Prerequisites
- Docker & Docker Compose installed

#### Quick Start

1. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   GITHUB_TOKEN=optional_token
   GROQ_API_KEY=your_groq_api_key_here
   ```

2. **Start the Container**
   ```bash
   docker-compose up -d
   ```

3. **Generate & Heal Tests Inside Container**
   ```bash
   docker exec playwright-ai-engine python generate.py "your test scenario" --name test_name --run
   ```

4. **View Live Reports**
   Open `playwright-report/index.html` in your browser

5. **Stop the Container**
   ```bash
   docker-compose down
   ```

#### Docker Benefits
✅ No local environment setup required  
✅ Consistent execution across machines  
✅ Pre-installed Playwright browsers  
✅ Automatic file sync to local machine  
✅ Isolated execution environment  

---

## 🎮 Usage Examples

### Example 1: Simple Test Generation
```bash
python generate.py "Navigate to playwright.dev and verify the page title" \
  --name verify_title \
  --run \
  --headed
```

### Example 2: With Auto-Healing (3 Retries)
```bash
python generate.py "Click the search button, enter 'locators', verify results" \
  --name search_test \
  --run \
  --headed \
  --retries 3
```

### Example 3: From BDD Feature File
```bash
# Features are automatically parsed and converted to Playwright tests
python generate.py features/search.feature \
  --name bdd_search_test \
  --run \
  --headed
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# Required
GROQ_API_KEY=your_api_key

# Optional
GITHUB_TOKEN=your_github_token
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright  # For Docker only
```

### Playwright Config (`playwright.config.ts`)

Modify `playwright.config.ts` to adjust:
- **Browser type** (chromium, firefox, webkit)
- **Base URL** for tests
- **Timeout settings**
- **Retry policies**
- **Reporter options**

### AI Prompts

Fine-tune test generation by editing:
- `prompts/generate_test.txt` - Controls how tests are generated
- `prompts/heal_test.txt` - Controls how broken tests are fixed
- `prompts/coding_standards.txt` - Code style guidelines

---

## 🩹 Self-Healing Deep Dive

The self-healing mechanism works as follows:

1. **Test Execution Failure Detected**
   - Playwright test fails with error message

2. **Error Analysis**
   - Generate captures the error log and test output
   - DOM is re-extracted from the target application

3. **AI-Powered Healing**
   - LLM analyzes the error, original test, and updated DOM
   - Generates corrected test code

4. **Retry Execution**
   - Updated test is run again
   - Process repeats until success or max retries reached

5. **Manual Intervention** (if needed)
   - Error is logged for developer review
   - Original test available for manual fixing

**Example Healing Scenarios:**
- ❌ Locator no longer exists → ✅ AI finds new selector
- ❌ Button text changed → ✅ AI updates text matcher
- ❌ Page navigation changed → ✅ AI adapts navigation flow
- ❌ Form validation changed → ✅ AI updates assertions

---

## 📊 Output Artifacts

After running tests, you'll find:

```
tests/generated/
  └── test_name.spec.ts         # Generated Playwright test

playwright-report/
  └── index.html                # Detailed test report with traces
```

Open the HTML report in your browser to:
- 📹 Watch test execution traces
- 🔍 Inspect DOM snapshots
- 📝 View detailed logs
- ✅ See pass/fail status

---

## 🚨 Troubleshooting

### Issue: "Playwright browsers not found"
**Solution:**
```bash
npx playwright install chromium
```

### Issue: "LLM API timeout"
**Solution:** Check your Groq API key and ensure it has sufficient quota

### Issue: "Docker permission denied"
**Solution:**
```bash
# On Linux/Mac, add your user to docker group:
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: "Generated tests still failing after healing"
**Solution:**
1. Check the `playwright-report/` for execution traces
2. Verify the target application is accessible
3. Review `prompts/generate_test.txt` and `heal_test.txt`
4. Consider increasing retry attempts with `--retries 5`

---

## 📚 API Reference

### CLI Arguments (generate.py)

```bash
python generate.py <feature_file_or_prompt> [options]

Arguments:
  feature_file_or_prompt    Feature file path or test scenario description

Options:
  --name NAME               Generated test file name (default: bdd_generated)
  --run                     Execute the test immediately after generation
  --headed                  Show browser during test execution
  --retries N               Number of self-healing retry attempts (default: 2)
```

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test with Docker for consistency
4. Submit a pull request

---

## 📄 License

ISC

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review test execution traces in `playwright-report/`
3. Examine generated test code in `tests/generated/`
4. Check error logs in terminal output
