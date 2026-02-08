import os
import requests

HF_API_URL = "https://api-inference.huggingface.co/models/defog/sqlcoder-7b-2"
HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def generate_sql(question, schema_context, sample_data=None):
    prompt = f"""
You are a SQL expert.
Convert the question to SQL.
Return only SQL.

Schema:
{schema_context}

Question:
{question}
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 128,
            "temperature": 0.0
        }
    }

    response = requests.post(
        HF_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    result = response.json()

    return result[0]["generated_text"].strip()
