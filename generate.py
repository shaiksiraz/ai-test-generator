import argparse
import subprocess
import sys
import os
from src.test_generator import generate_test

def run_playwright(test_file: str, headed: bool = False):
    """Executes the newly generated Playwright test."""
    use_shell = os.name == "nt"
    
    cmd = ["npx", "playwright", "test", f"tests/generated/{test_file}.spec.ts"]
    
    # Inject the headed flag if requested
    if headed:
        cmd.append("--headed")
    
    try:
        subprocess.run(cmd, check=True, shell=use_shell)
    except subprocess.CalledProcessError:
        print("\n❌ Playwright test failed. Check the output above.")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: Could not find 'npx'. Ensure Node.js is installed and in your PATH.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Test Generator for Playwright")
    parser.add_argument("steps", type=str, help="Plain English steps for the test scenario")
    parser.add_argument("--name", type=str, default="ai_generated", help="Name of the generated test file")
    parser.add_argument("--run", action="store_true", help="Automatically run the test after generation")
    parser.add_argument("--headed", action="store_true", help="Run Playwright in headed mode (UI visible)")

    args = parser.parse_args()

    generate_test(args.steps, args.name)

    if args.run:
        print("\n🚀 Running Playwright test...\n")
        run_playwright(args.name, args.headed)