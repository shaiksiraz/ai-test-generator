import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def encode_image(image_path: str) -> str:
    """Reads an image file and converts it to a Base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ask_llm(prompt: str, image_path: str = None) -> str:
    """
    Sends the prompt (and optional image) to the Primary API (GitHub Models). 
    If it fails, automatically routes to the Fallback API.
    """
    
    # 1. Setup Primary Credentials (GitHub Models)
    github_token = os.getenv("GITHUB_TOKEN")
    github_model = os.getenv("GITHUB_MODEL_NAME", "gpt-4o")
    
    # 2. Setup Fallback Credentials
    fallback_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
    fallback_model = os.getenv("OPENAI_MODEL_NAME", "llama-3.3-70b-versatile")
    fallback_base = os.getenv("OPENAI_BASE_URL")

    # 3. Build the User Message Content (Text vs. Multimodal)
    if image_path and os.path.exists(image_path):
        print(f"📸 Attaching crash screenshot to AI context: {image_path}")
        base64_image = encode_image(image_path)
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ]
    else:
        # If no image is provided, we default to the standard text string
        user_content = prompt

    # --- PRIMARY EXECUTION ---
    if github_token:
        try:
            print(f"🔌 Routing request to Primary API: GitHub Models ({github_model})...")
            
            client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=github_token
            )
            
            response = client.chat.completions.create(
                model=github_model,
                messages=[
                    {"role": "system", "content": "You are a strict, enterprise-grade test automation architect."},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"\n⚠️ Primary API (GitHub) failed: {e}")
            print(f"🔄 Triggering Failover to Backup API ({fallback_model})...\n")
    
    # --- FALLBACK EXECUTION ---
    if not fallback_key:
        raise ValueError("❌ FATAL: Both Primary and Fallback APIs failed. Check your .env keys.")
        
    print(f"🔌 Routing request to Fallback API ({fallback_model})...")
    
    # Architect Warning: If falling back to a text-only model like Llama 3 while holding an image, 
    # the API will likely reject it. We pass it through anyway to let the API handle the error natively.
    if image_path and "llama" in fallback_model.lower():
        print("⚠️ WARNING: Fallback model appears to be text-only, but an image is attached. This may fail.")

    client_args = {"api_key": fallback_key}
    if fallback_base:
         client_args["base_url"] = fallback_base
         
    client = OpenAI(**client_args)
    
    response = client.chat.completions.create(
        model=fallback_model,
        messages=[
            {"role": "system", "content": "You are a strict, enterprise-grade test automation architect."},
            {"role": "user", "content": user_content}
        ],
        temperature=0.1
    )
    
    return response.choices[0].message.content