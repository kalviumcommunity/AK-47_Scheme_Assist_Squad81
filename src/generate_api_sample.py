# -*- coding: utf-8 -*-
"""Generate sample API request and response for MSU 3.44."""
import json
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)
payload = {"question": "What is the annual financial assistance provided under PM-KISAN?"}
response = client.post("/query", json=payload)

data = {
    "request": {
        "method": "POST",
        "url": "http://localhost:8000/query",
        "headers": {"Content-Type": "application/json"},
        "body": payload,
    },
    "response": {
        "status_code": response.status_code,
        "body": response.json(),
    },
}

with open("outputs/api_sample_query_response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

lines = [
    "================================================================================",
    "  SchemeAssist RAG Service - Sample API Request & Structured Response",
    "================================================================================",
    "",
    "REQUEST:",
    'curl -X POST http://localhost:8000/query \\',
    '  -H "Content-Type: application/json" \\',
    f"  -d '{json.dumps(payload)}'",
    "",
    f"RESPONSE (HTTP {response.status_code} OK):",
    json.dumps(response.json(), indent=2),
    "",
    "================================================================================",
]

with open("outputs/api_sample_query_response.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("Generated sample request and response artifacts successfully.")
