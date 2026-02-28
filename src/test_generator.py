import re
from pathlib import Path
from src.llm_client import ask_llm
from src.dom_extractor import extract_url_from_prompt, get_clean_dom

PROMPT_FILE = Path("prompts/generate_test.txt")
OUTPUT_DIR = Path("tests/generated")

def clean_code_output(raw_output: str) -> str:
    """Strips markdown code blocks (```typescript ... ```) from the LLM output."""
    pattern = r"^```(?:typescript|ts)?\n(.*?)\n```$"
    match = re.search(pattern, raw_output.strip(), re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return raw_output.strip()

def generate_test(steps: str, test_name: str = "ai_generated"):
    template = PROMPT_FILE.read_text(encoding="utf-8")
    
    # --- NEW: Context Injection Logic ---
    url = extract_url_from_prompt(steps)
    dom_context = "No DOM context available."
    
    if url:
        dom_context = get_clean_dom(url)
    else:
        print("⚠️ No URL found in prompt. LLM will guess locators without DOM context.")
    # ------------------------------------

    # Inject BOTH the steps and the scraped HTML into the prompt
    prompt = template.replace("{steps}", steps).replace("{dom_context}", dom_context)

    print(f"🧠 Consulting LLM to write: {test_name}.spec.ts...")
    raw_code = ask_llm(prompt)
    
    clean_code = clean_code_output(raw_code)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sanitize test name to ensure it's a valid filename
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', test_name).lower()
    file_path = OUTPUT_DIR / f"{safe_name}.spec.ts"
    
    file_path.write_text(clean_code, encoding="utf-8")
    print(f"✅ Test successfully generated and saved at: {file_path}")