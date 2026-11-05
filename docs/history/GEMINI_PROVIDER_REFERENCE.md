> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Gemini 4 Argon — API Usage Guide & Reference

This guide explains how to connect to, authenticate, and query **Gemini 4 Argon** (`gemini-4-argon`) via Google's **Gemini Enterprise Agent Platform API**.

---

## 1. Quickstart & Configuration

Your credentials and endpoint parameters are configured in [`.env`](file:///d:/Code%20Projects/Job%20Search/.env):

```env
GOOGLE_API_KEY=<set locally in .env>
GOOGLE_CLOUD_PROJECT=1033995202395
GOOGLE_CLOUD_LOCATION="global"
API_ENDPOINT="https://aiplatform.googleapis.com"
MODEL_ID="gemini-4-argon"
GENERATE_CONTENT_API="generateContent"
```

> [!IMPORTANT]
> **Why `locations/global` is required**:
> The `gemini-4-argon` model is hosted on Google Cloud's global enterprise routing layer. Calling a local region (e.g. `us-central1` or `asia-southeast1`) directly returns `404 Not Found`. Always route through `locations/global`.

---

## 2. Running the Python Test Client

A ready-to-use, dependency-free Python client has been provided in [`gemini_client.py`](file:///d:/Code%20Projects/Job%20Search/gemini_client.py).

To execute the test suite (testing token counting, text generation, and serverless code execution):

```powershell
python gemini_client.py
```

### Python Code Usage Example

```python
from gemini_client import GeminiArgonClient

# 1. Initialize client (automatically loads credentials from .env)
client = GeminiArgonClient()

# 2. Pre-calculate token cost
cost_info = client.count_tokens("Explain quantum computing in 2 sentences.")
print(f"Estimated Cost: ${cost_info['estimated_cost_usd']:.6f}")

# 3. Generate text with Tunable Reasoning ('LOW', 'MEDIUM', 'HIGH')
response = client.generate(
    prompt="Explain how distributed caching works.",
    thinking_level="HIGH"
)
print(response["text"])

# 4. Run with Built-in Serverless Python Execution Sandbox
code_result = client.run_with_code_execution(
    "Calculate the 25th Fibonacci number using Python."
)
print("Code Executed:", code_result["generated_code"])
print("Sandbox Output:", code_result["execution_output"])
print("Final Answer:", code_result["final_answer"])
```

---

## 3. Direct cURL Examples

### A. Standard Text Generation (`generateContent`)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GOOGLE_API_KEY" \
  "https://aiplatform.googleapis.com/v1/projects/1033995202395/locations/global/publishers/google/models/gemini-4-argon:generateContent" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{"text": "Summarize the key benefits of microservices architecture."}]
      }
    ],
    "generation_config": {
      "thinking_config": {
        "thinking_level": "MEDIUM"
      }
    }
  }'
```

### B. Built-in Serverless Python Execution (`tools.code_execution`)

Google executes the code inside a cloud sandbox and feeds the output directly to the model:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GOOGLE_API_KEY" \
  "https://aiplatform.googleapis.com/v1/projects/1033995202395/locations/global/publishers/google/models/gemini-4-argon:generateContent" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{"text": "Calculate the sum of primes below 100 in Python."}]
      }
    ],
    "tools": [
      {"code_execution": {}}
    ]
  }'
```

### C. Real-Time Streaming (`streamGenerateContent`)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GOOGLE_API_KEY" \
  "https://aiplatform.googleapis.com/v1/projects/1033995202395/locations/global/publishers/google/models/gemini-4-argon:streamGenerateContent?alt=sse" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{"text": "Write a short poem about coding."}]
      }
    ]
  }'
```

---

## 4. Billing and credits

Billing rates and credit eligibility must be verified in the Google Cloud account.
The endpoint alone does not establish that promotional credits cover a request.
The application records provider usage counters and makes no guaranteed cost/credit claim.

---

## 5. Troubleshooting & FAQ

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `404 Not Found: Publisher model ... was not found` | The URL did not include `/locations/global/` or used an unprovisioned model name. | Ensure the URL includes `/locations/global/publishers/google/models/gemini-4-argon`. |
| `403 Forbidden: SERVICE_DISABLED` | Attempting to query `generativelanguage.googleapis.com` (AI Studio) instead of the Enterprise Agent Platform. | Direct all queries to `aiplatform.googleapis.com`. |
| `requests.exceptions.ConnectionError` | Network sandbox or proxy issue. | Verify internet connectivity or run unsandboxed in terminal. |
