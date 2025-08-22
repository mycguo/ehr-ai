import vertexai
from vertexai.generative_models import GenerativeModel
import os

vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ["GOOGLE_CLOUD_LOCATION"])

model = GenerativeModel("gemini-2.5-pro")

def ask_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text
