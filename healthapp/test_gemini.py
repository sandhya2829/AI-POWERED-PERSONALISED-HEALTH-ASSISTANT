import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

try:
    prompt = "Give a simple healthy breakfast diet plan"
    response = model.generate_content(prompt)
    print("Gemini working properly:")
    print(response.text.strip())
except Exception as e:
    print("Gemini ERROR:")
    print(str(e))
