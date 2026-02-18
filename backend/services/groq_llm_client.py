import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


# Load .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")


# Initialize Groq Client
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ✅ Updated model
MODEL_NAME = "llama-3.1-8b-instant"


def generate_sql(question: str, schema_context: str, sample_data: str = None) -> dict:

    prompt = f"""You are an expert SQL generator.

Generate ONLY a valid SQL query.
Do not explain anything.
Do not add markdown.
Do not add comments.

Schema:
{schema_context}

Question:
{question}
"""

    if sample_data:
        prompt += f"\nSample Data:\n{sample_data}\n"

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=256
        )

        raw_text = response.choices[0].message.content.strip()
        sql = extract_sql(raw_text)

        return {
            "success": True,
            "sql": sql,
            "raw": raw_text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sql": None
        }


def extract_sql(text: str) -> str:

    if "```sql" in text:
        text = text.split("```sql")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    text = text.strip()

    if ";" in text:
        text = text.split(";")[0] + ";"

    return text.strip()
