import re
from pathlib import Path
from src.llm_client import ask_llm
from src.dom_extractor import extract_url_from_feature, get_clean_dom

PROMPT_FILE = Path("prompts/generate_test.txt")
STANDARDS_FILE = Path("prompts/coding_standards.txt")

def generate_test(feature_content: str, test_name: str = "bdd_generated"):
    # Read both files
    template = PROMPT_FILE.read_text(encoding="utf-8")
    system_context = STANDARDS_FILE.read_text(encoding="utf-8")
    
    url = extract_url_from_feature(feature_content)
    dom_context = "No DOM context available."
    
    if url:
        dom_context = get_clean_dom(url)
    else:
        print("⚠️ No URL found in Given step. LLM will guess locators without DOM context.")

    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', test_name).lower()
    
    # --- 🧹 NEW: CLEANUP GHOST FILES ---
    expected_pom = Path(f"pageObjects/{safe_name}Page.ts")
    expected_spec = Path(f"tests/generated/{safe_name}.spec.ts")

    if expected_pom.exists():
        expected_pom.unlink()
        print(f"🗑️ Deleted old POM: {expected_pom}")
    
    if expected_spec.exists():
        expected_spec.unlink()
        print(f"🗑️ Deleted old Spec: {expected_spec}")
    # -----------------------------------
    
    system_context_formatted = system_context.replace("{test_name}", safe_name)
    
    prompt = template.replace("{system_context}", system_context_formatted)\
                     .replace("{feature_content}", feature_content)\
                     .replace("{dom_context}", dom_context)\
                     .replace("{test_name}", safe_name)

    print(f"🧠 Translating BDD Feature into Page Object Model architecture...")
    raw_code = ask_llm(prompt)
    
    file_blocks = re.split(r'### FILE:\s*', raw_code)[1:] 
    
    if not file_blocks:
        print("❌ Error: LLM did not format the output with '### FILE:' tags. Check the prompt.")
        return

    for block in file_blocks:
        parts = block.split('\n', 1)
        if len(parts) < 2:
            continue
            
        file_path_str = parts[0].strip()
        code_content = parts[1].strip()
        
        # Extract ONLY what is inside the ```typescript ... ``` blocks
        match = re.search(r'```(?:typescript|ts)?\n(.*?)```', code_content, re.DOTALL)
        
        if match:
            code_content = match.group(1).strip()
        else:
            # Fallback in case the LLM forgot backticks entirely
            code_content = code_content.strip()

        target_path = Path(file_path_str)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        target_path.write_text(code_content, encoding="utf-8")
        print(f"✅ Generated and saved: {target_path}")