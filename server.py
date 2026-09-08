# server.py
# ====== Usage ======
# uv venv
# source .venv/bin/activate
# uv pip install -r requirements.txt
# python server.py
# http://127.0.0.1:8000/

import subprocess
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
CLI_COMMAND = "your-ai-cli"

class Request(BaseModel):
    messages: list

def handshake():
    return {"status": "ok"}

def ask(messages):
    prompt = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in messages
    )
    result = subprocess.run(
        [CLI_COMMAND, prompt],
        capture_output=True,
        text=True
    )
    if result.returncode:
        raise Exception(result.stderr)

    return {"content": result.stdout}

@app.get("/")
def root():
    return handshake()

@app.post("/ask")
def handle_ask(request: Request):
    return ask(request.messages)

def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
