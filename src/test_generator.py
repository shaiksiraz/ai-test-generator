import re
from pathlib import Path
from src.llm_client import ask_llm
from src.dom_extractor import extract_url_from_feature, get_clean_dom
import subprocess
import sys

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
    
    expected_pom = Path(f"pageObjects/{safe_name}Page.ts")
    expected_spec = Path(f"tests/generated/{safe_name}.spec.ts")

    # --- 🛡️ NEW: @stable TAG CHECK ---
    if "@stable" in feature_content and expected_pom.exists() and expected_spec.exists():
        print(f"🛡️ '@stable' tag detected. Skipping AI generation and using existing files.")
        return safe_name, dom_context
    # ---------------------------------

    # --- 🧹 CLEANUP GHOST FILES ---
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
    return safe_name, dom_context

def run_and_heal(test_file_path: str, retries: int = 2):
    """Runs the Playwright test and triggers self-healing if it fails."""
    
    for attempt in range(retries + 1):
        print(f"\n🚀 Running Playwright test (Attempt {attempt + 1}/{retries + 1})...")
        
        # Use subprocess to CAPTURE the terminal output
        result = subprocess.run(
            ["npx", "playwright", "test", test_file_path, "--headed"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Test Passed Successfully!")
            print(result.stdout)
            return True # Exit the loop, we are done!
            
        else:
            print(f"❌ Test Failed!")
            error_log = result.stderr if result.stderr else result.stdout
            
            # Print a snippet of the error so you can see it
            print("--- ERROR LOG CAUGHT ---")
            print(error_log[:1000] + "...\n") 
            
            if attempt < retries:
                print("🩹 Initiating Self-Healing Protocol...")
                # TODO: We will call the AI with heal_test.txt here!
            else:
                print("💀 Self-Healing Exhausted. Manual intervention required.")
                return False

# Example usage at the bottom of your generate.py:
# if args.run:
#     run_and_heal("tests/generated/search_bdd.spec.ts")        
HEAL_PROMPT_FILE = Path("prompts/heal_test.txt")

def heal_test(safe_name: str, error_log: str, dom_context: str):
    """Feeds the broken code and error log back to the AI for self-healing."""
    
    pom_path = Path(f"pageObjects/{safe_name}Page.ts")
    spec_path = Path(f"tests/generated/{safe_name}.spec.ts")
    
    # 1. Gather the broken code
    current_code = ""
    if pom_path.exists():
        current_code += f"### FILE: {pom_path}\n```typescript\n{pom_path.read_text(encoding='utf-8')}\n```\n\n"
    if spec_path.exists():
        current_code += f"### FILE: {spec_path}\n```typescript\n{spec_path.read_text(encoding='utf-8')}\n```\n"

    # 2. Read Prompts
    template = HEAL_PROMPT_FILE.read_text(encoding="utf-8")
    system_context = STANDARDS_FILE.read_text(encoding="utf-8").replace("{test_name}", safe_name)
    
    # 3. Build the Healing Prompt
    prompt = template.replace("{system_context}", system_context)\
                     .replace("{dom_context}", dom_context)\
                     .replace("{error_log}", error_log)\
                     .replace("{current_code}", current_code)

    print(f"🧠 AI is analyzing the Error Log and generating a patch...")
    raw_code = ask_llm(prompt)
    
    # 4. Parse and Overwrite (Same bulletproof parser as generation)
    file_blocks = re.split(r'### FILE:\s*', raw_code)[1:] 
    
    if not file_blocks:
        print("❌ Error: AI failed to format the healed code correctly.")
        return False

    for block in file_blocks:
        parts = block.split('\n', 1)
        if len(parts) < 2:
            continue
            
        file_path_str = parts[0].strip()
        code_content = parts[1].strip()
        
        match = re.search(r'```(?:typescript|ts)?\n(.*?)```', code_content, re.DOTALL)
        code_content = match.group(1).strip() if match else code_content.strip()

        target_path = Path(file_path_str)
        target_path.write_text(code_content, encoding="utf-8") # Overwrites the broken file
        print(f"🩹 Healed and overwritten: {target_path}")
        
    return True