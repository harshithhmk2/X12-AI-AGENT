import json
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze(validation_result):
    """
    Generate AI analysis based on 997-aware validation result
    """

    all_errors = validation_result.get("all_errors", [])
    fatal_errors = validation_result.get("fatal_errors", [])
    ack_status = validation_result.get("ack_status", "UNKNOWN")

    prompt = f"""
You are an EDI X12 expert.

Transaction: {validation_result.get("transaction")}
997 Acknowledgment Status: {ack_status}

Fatal Errors (cause rejection):
{json.dumps(fatal_errors, indent=2)}

All Validation Errors (rule + comparison):
{json.dumps(all_errors, indent=2)}

Provide a detailed, structured analysis with:
1. Root cause summary
2. Business impact
3. How to fix
4. Severity reasoning
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content
