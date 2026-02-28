import argparse
import subprocess
import sys
import os
import re
from pathlib import Path
from src.test_generator import generate_test

def run_playwright(test_file: str, headed: bool = False):
    """Executes the Playwright test."""
    use_shell = os.name == "nt"
    target_file = f"tests/generated/{test_file}.spec.ts"
    
    cmd = ["npx", "playwright", "test", target_file]
    
    if headed:
        cmd.append("--headed")
    
    try:
        subprocess.run(cmd, check=True, shell=use_shell)
    except subprocess.CalledProcessError:
        print("\n❌ Playwright test failed. Check the output above.")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: Could not find 'npx'. Ensure Node.js is installed.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Test Generator for Playwright")
    parser.add_argument("feature_file", type=str, help="Path to the .feature file")
    parser.add_argument("--name", type=str, default="bdd_generated", help="Name of the generated test file")
    parser.add_argument("--run", action="store_true", help="Automatically run the test after generation")
    parser.add_argument("--headed", action="store_true", help="Run Playwright in headed mode (UI visible)")

    args = parser.parse_args()

    file_path = Path(args.feature_file)
    if not file_path.exists():
        print(f"❌ Error: Could not find file at '{args.feature_file}'")
        sys.exit(1)
        
    feature_content = file_path.read_text(encoding="utf-8")

    # 🛠️ THE NEW ARCHITECTURE: State-Aware Generation
    is_stable = "@stable" in feature_content
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', args.name).lower()
    target_spec_path = Path(f"tests/generated/{safe_name}.spec.ts")

    if is_stable and target_spec_path.exists():
        print(f"\n🛡️  Feature is marked @stable. Skipping AI generation to protect '{safe_name}.spec.ts'...")
    else:
        # Only call the LLM and overwrite if NOT stable, or if the file doesn't exist yet
        generate_test(feature_content, args.name)

    if args.run:
        print("\n🚀 Running Playwright test...\n")
        run_playwright(safe_name, args.headed)