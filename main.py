#=== main.py
# 使い方:
#   index.htmlからPyodideで読み込む
#===

import json
from js import document, fetch

model_el = document.getElementById("model")
port_el = document.getElementById("port")
input_el = document.getElementById("input")
messages_el = document.getElementById("messages")
sites = {}


async def load_sites():
    global sites
    response = await fetch("sites.json")
    sites = json.loads(await response.text())
    model_el.innerHTML = ""
    for name in sites:
        if name == "default":
            continue
        option = document.createElement("option")
        option.value = name
        option.textContent = name
        model_el.appendChild(option)


async def send_message(event):
    event.preventDefault()
    text = input_el.value.strip()
    if not text:
        return
    input_el.value = ""
    model = model_el.value
    port = port_el.value
    messages_el.innerHTML += f"<div>YOU: {text}</div><div>MODEL: {model}:{port}</div>"


document.getElementById("inputForm").onsubmit = send_message
await load_sites()
