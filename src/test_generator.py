import re
from pathlib import Path
from src.llm_client import ask_llm
from src.dom_extractor import extract_url_from_feature, get_clean_dom

PROMPT_FILE = Path("prompts/generate_test.txt")
STANDARDS_FILE = Path("prompts/coding_standards.txt") # 🛠️ NEW: Reference the global standards

def generate_test(feature_content: str, test_name: str = "bdd_generated"):
    # Read both files
    template = PROMPT_FILE.read_text(encoding="utf-8")
    system_context = STANDARDS_FILE.read_text(encoding="utf-8") # 🛠️ NEW: Read the standards
    
    url = extract_url_from_feature(feature_content)
    dom_context = "No DOM context available."
    
    if url:
        dom_context = get_clean_dom(url)
    else:
        print("⚠️ No URL found in Given step. LLM will guess locators without DOM context.")

    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', test_name).lower()
    
    # 🛠️ NEW: Inject the system_context and dynamically replace the {test_name} inside the standards too!
    system_context_formatted = system_context.replace("{test_name}", safe_name)
    
    prompt = template.replace("{system_context}", system_context_formatted)\
                     .replace("{feature_content}", feature_content)\
                     .replace("{dom_context}", dom_context)\
                     .replace("{test_name}", safe_name)

    print(f"🧠 Translating BDD Feature into Page Object Model architecture...")
    raw_code = ask_llm(prompt)
    
    print(f"🧠 Translating BDD Feature into Page Object Model architecture...")
    raw_code = ask_llm(prompt)
    
    # 🛠️ DEBUG: Print the raw AI response to the terminal
    print("\n" + "="*40)
    print("RAW LLM OUTPUT:")
    print(raw_code)
    print("="*40 + "\n")
    
    # We now pass the safe_name to the prompt...
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
        
        code_content = re.sub(r'^```(?:typescript|ts)?\n', '', code_content, flags=re.MULTILINE)
        code_content = re.sub(r'\n```$', '', code_content).strip()

        target_path = Path(file_path_str)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        target_path.write_text(code_content, encoding="utf-8")
        print(f"✅ Generated and saved: {target_path}")