import json
from js import fetch

URL = "http://127.0.0.1:8000/ask"

async def call_cli(messages):
    response = await fetch(URL, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"messages": messages})
    })
    if not response.ok:
        raise Exception(f"Agent error: {response.status}")
    return json.loads(await response.text())["content"]
