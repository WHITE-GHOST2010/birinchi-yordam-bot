import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

models_to_test = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

for model in models_to_test:
    print(f"\nModelni sinab ko'rish: {model}...")
    try:
        response = client.models.generate_content(
            model=model,
            contents="Salom! 1+1 necha?"
        )
        print(f"✅ {model} muvaffaqiyatli ishladi!")
        print(f"Javob: {response.text}")
    except Exception as e:
        print(f"❌ {model} ishlamadi. Xatolik: {e}")