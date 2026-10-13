import os

from dotenv import load_dotenv
from groq import Groq


class GroqProvider:
    """Groq LLM integration for AGASTYA."""

    def __init__(self, api_key: str, model: str) -> None:
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        result = response.choices[0].message.content

        if not result:
            raise RuntimeError("Groq returned an empty response.")

        return result


def create_provider() -> GroqProvider:
    """Load the Groq configuration and create a provider."""

    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b",
    )

    if not api_key or api_key == "YOUR_ACTUAL_GROQ_API_KEY":
        raise ValueError("GROQ_API_KEY is missing. Configure it in your .env file.")

    return GroqProvider(
        api_key=api_key,
        model=model,
    )
