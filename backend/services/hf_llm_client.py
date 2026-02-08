from transformers import pipeline

MODEL_NAME = "defog/sqlcoder-7b-2"
generator = pipeline("text-generation", model=MODEL_NAME, max_new_tokens=128)

def generate_sql(question, schema_context, sample_data=None):
    prompt = f"""You are a SQL expert. Convert the following question to a valid SQL query based on this schema. Respond only with the SQL.

Schema:
{schema_context}
"""
    if sample_data:
        prompt += f"\nSample data:\n{sample_data}\n"
    prompt += f"\nQuestion:\n{question}\n"
    result = generator(prompt, max_new_tokens=128)[0]["generated_text"]
    return result.strip()