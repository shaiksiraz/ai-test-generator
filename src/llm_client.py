import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def ask_llm(prompt: str) -> str:
    """
    Sends the prompt to the Primary API (GitHub Models). 
    If it fails, automatically routes to the Fallback API.
    """
    
    # 1. Setup Primary Credentials (GitHub Models)
    github_token = os.getenv("GITHUB_TOKEN")
    github_model = os.getenv("GITHUB_MODEL_NAME", "gpt-4o")
    
    # 2. Setup Fallback Credentials
    fallback_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
    fallback_model = os.getenv("OPENAI_MODEL_NAME", "llama-3.3-70b-versatile")
    fallback_base = os.getenv("OPENAI_BASE_URL")

    # --- PRIMARY EXECUTION ---
    if github_token:
        try:
            print(f"🔌 Routing request to Primary API: GitHub Models ({github_model})...")
            
            # GitHub Models uses the Azure Inference endpoint
            client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=github_token
            )
            
            response = client.chat.completions.create(
                model=github_model,
                messages=[
                    {"role": "system", "content": "You are a strict, enterprise-grade test automation architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1 # Keep temperature low for deterministic code generation
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"\n⚠️ Primary API (GitHub) failed: {e}")
            print(f"🔄 Triggering Failover to Backup API ({fallback_model})...\n")
    
    # --- FALLBACK EXECUTION ---
    if not fallback_key:
        raise ValueError("❌ FATAL: Both Primary and Fallback APIs failed. Check your .env keys.")
        
    print(f"🔌 Routing request to Fallback API ({fallback_model})...")
    
    client_args = {"api_key": fallback_key}
    if fallback_base:
         client_args["base_url"] = fallback_base
         
    client = OpenAI(**client_args)
    
    response = client.chat.completions.create(
        model=fallback_model,
        messages=[
            {"role": "system", "content": "You are a strict, enterprise-grade test automation architect."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    return response.choices[0].message.content