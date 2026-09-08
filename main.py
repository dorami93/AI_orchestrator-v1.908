import asyncio
import json
from js import document, localStorage, fetch

from call_cli_llm import call_cli
from output import render_messages


input_el = document.getElementById("input")
messages_el = document.getElementById("messages")
settings = document.getElementById("settingsModal")
model = document.getElementById("modelInput")
temperature = document.getElementById("temperatureInput")
tokens = document.getElementById("tokensInput")
json_input = document.getElementById("jsonInput")

messages = []
schema = None


async def load_models():
    response = await fetch("models.json")
    models = json.loads(await response.text())

    model.innerHTML = ""
    for model_id in models:
        option = document.createElement("option")
        option.value = option.textContent = model_id
        model.appendChild(option)

    model.value = localStorage.getItem("model") or models[0]


def open_settings(*_):
    temperature.value = localStorage.getItem("temperature") or "0"
    tokens.value = localStorage.getItem("tokens") or "2000"
    asyncio.ensure_future(load_models())
    settings.classList.remove("hidden")


def save_settings(*_):
    localStorage.setItem("model", model.value)
    localStorage.setItem("temperature", temperature.value)
    localStorage.setItem("tokens", tokens.value)
    settings.classList.add("hidden")


def close_settings(*_):
    settings.classList.add("hidden")


async def select_json(event):
    global schema
    file = event.target.files.item(0)
    if not file:
        schema = None
        return
    try:
        schema = json.loads(await file.text())
    except Exception:
        schema = None


async def edit_message():
    text = input_el.value.strip()
    if not text:
        return

    input_el.value = ""
    messages.append({"role": "user", "content": text})
    render_messages(messages_el, messages)

    try:
        result = await call_cli(messages)
        messages.append({"role": "assistant", "content": result})
    except Exception as e:
        messages.append({"role": "assistant", "content": "エラー: " + str(e)})

    render_messages(messages_el, messages)


def submit(event):
    event.preventDefault()
    asyncio.ensure_future(edit_message())


def bind(el, attr, handler):
    if el:
        setattr(el, attr, handler)


bind(document.getElementById("inputForm"), "onsubmit", submit)
bind(document.getElementById("settingsBtn"), "onclick", open_settings)
bind(document.getElementById("saveSettingsBtn"), "onclick", save_settings)
bind(document.getElementById("closeSettingsBtn"), "onclick", close_settings)
bind(json_input, "onchange", lambda e: asyncio.ensure_future(select_json(e)))
