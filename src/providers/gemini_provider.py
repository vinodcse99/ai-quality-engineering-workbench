
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class GeminiProvider:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Configure it in the project .env file."
            )

        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt):

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=300
            )
        )

        generated_text = response.text

        if not generated_text or not generated_text.strip():
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return generated_text.strip()

    def close(self):
        self.client.close()
