import re
from pathlib import Path
from src.llm_client import ask_llm
from src.dom_extractor import extract_url_from_feature, get_clean_dom

PROMPT_FILE = Path("prompts/generate_test.txt")
# We are still saving to this folder, but since we updated .gitignore, Git will now track these files!
OUTPUT_DIR = Path("tests/generated") 

def clean_code_output(raw_output: str) -> str:
    """Aggressively hunts for the TypeScript code block and ignores all other text."""
    # Removed the strict ^ and $ boundaries so it finds the block anywhere in the response
    match = re.search(r'```(?:typescript|ts)?\n(.*?)\n```', raw_output, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # If no markdown block is found, return the raw output as a fallback
    return raw_output.strip()

def generate_test(feature_content: str, test_name: str = "bdd_generated"):
    template = PROMPT_FILE.read_text(encoding="utf-8")
    
    # Context Injection Logic - Now driven by the Gherkin 'Given' step
    url = extract_url_from_feature(feature_content)
    dom_context = "No DOM context available."
    
    if url:
        dom_context = get_clean_dom(url)
    else:
        print("⚠️ No URL found in Given step. LLM will guess locators without DOM context.")

    prompt = template.replace("{feature_content}", feature_content).replace("{dom_context}", dom_context)

    print(f"🧠 Translating BDD Feature to Playwright: {test_name}.spec.ts...")
    raw_code = ask_llm(prompt)
    
    clean_code = clean_code_output(raw_code)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', test_name).lower()
    file_path = OUTPUT_DIR / f"{safe_name}.spec.ts"
    
    file_path.write_text(clean_code, encoding="utf-8")
    print(f"✅ BDD Test successfully generated and saved at: {file_path}")