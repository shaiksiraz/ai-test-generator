import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initializes automatically using the .env variables.
# It seamlessly routes to Groq because of OPENAI_BASE_URL.
client = OpenAI()
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "llama3-70b-8192")

def ask_llm(prompt: str) -> str:
    """Sends a prompt to the LLM and returns the text response."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a specialized code generation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1, # Low temperature for more predictable, deterministic code
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error communicating with LLM: {e}")
        raise