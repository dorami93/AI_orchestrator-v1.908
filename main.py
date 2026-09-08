import asyncio
from js import document

from call_cli_llm import call_cli
from output import render_messages


input_el = document.getElementById("input")
messages_el = document.getElementById("messages")

messages = []


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


def bind(el_id, el, attr, handler):
    if el is None:
        print(f"[warn] element #{el_id} not found; skipping binding")
        return
    setattr(el, attr, handler)


bind("inputForm", document.getElementById("inputForm"), "onsubmit", submit)
