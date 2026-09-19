import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

models_to_test = [
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash"
]

for model in models_to_test:
    print(f"\nModel: {model}...")
    try:
        response = client.models.generate_content(
            model=model,
            contents="Salom! 1+1?"
        )
        print(f"SUCCESS: {model} worked!")
        print(f"Result: {response.text.strip()}")
    except Exception as e:
        print(f"FAILED: {model} failed. Error: {e}")