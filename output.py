from js import document, marked


def render_messages(element, messages):
    element.innerHTML = ""

    for message in messages:
        div = document.createElement("div")
        div.className = "msg " + message["role"]
        div.innerHTML = marked.parse(message["content"])
        element.appendChild(div)

    element.scrollTop = element.scrollHeight
