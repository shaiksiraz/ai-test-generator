import argparse
from src.test_generator import generate_test, heal_test
import subprocess

def run_and_heal(safe_name: str, dom_context: str, retries: int = 2):
    test_file_path = f"tests/generated/{safe_name}.spec.ts"
    
    for attempt in range(retries + 1):
        print(f"\n🚀 Running Playwright test (Attempt {attempt + 1}/{retries + 1})...")
        
        
        # Use subprocess to CAPTURE the terminal output
        result = subprocess.run(
            ["npx", "playwright", "test", test_file_path, "--headed"],
            capture_output=True,
            text=True,
            shell=True  # <--- ADD THIS LINE
        )
        
        if result.returncode == 0:
            print("✅ Test Passed Successfully!")
            return 
            
        else:
            print(f"❌ Test Failed!")
            error_log = result.stderr if result.stderr else result.stdout
            
            print("--- ERROR LOG CAUGHT ---")
            print(error_log[:800] + "...\n") 
            
            if attempt < retries:
                print("🩹 Initiating Self-Healing Protocol...")
                # CALL THE AI TO HEAL THE FILES
                success = heal_test(safe_name, error_log, dom_context)
                if not success:
                    print("💀 Self-Healing pipeline aborted due to parsing error.")
                    break
            else:
                print("💀 Self-Healing Exhausted. Manual intervention required.")

# --- Execution Entry Point ---
# Update your arg parsing execution block to capture the returned variables:
if __name__ == "__main__":
    import argparse
    
    # 1. Setup the arguments so Python understands '--run', '--name', etc.
    parser = argparse.ArgumentParser(description="AI Playwright Test Generator & Healer")
    parser.add_argument("feature", help="Path to the BDD feature file")
    parser.add_argument("--name", default="bdd_generated", help="Name of the test suite")
    parser.add_argument("--run", action="store_true", help="Execute the test after generation")
    parser.add_argument("--headed", action="store_true", help="Run Playwright in headed mode")
    
    args = parser.parse_args()
    
    # 2. Read the feature file
    with open(args.feature, "r", encoding="utf-8") as f:
        feature_content = f.read()
        
    # 3. Generate the initial test code
    safe_name, dom_context = generate_test(feature_content, args.name)
    
    # 4. Trigger the Execution and Self-Healing Loop if '--run' is passed
    if args.run:
        run_and_heal(safe_name, dom_context)