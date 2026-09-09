# ============================================================
# call_cli_llm.py
#
# server.py に接続する軽量クライアント。
# 事前に別ターミナルで server.py を起動しておくこと。
#
# Run:
#   python3 call_cli_llm.py -url "https://chatgpt.com"
#
# 終了: exit
# ============================================================

import argparse
import json
import socket
import uuid

HOST, PORT = "127.0.0.1", 8765


def send_request(session_id, url, text):
    with socket.create_connection((HOST, PORT)) as sock:
        sock.sendall((json.dumps({"session_id": session_id, "url": url, "text": text}) + "\n").encode())
        raw = sock.recv(65536)
        return json.loads(raw.decode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", required=True)
    url = parser.parse_args().url
    session_id = uuid.uuid4().hex[:8]

    print(f"接続先: {url} (session: {session_id})")
    print("終了: exit\n")

    while True:
        text = input("> ").strip()
        if not text:
            continue
        if text.lower() == "exit":
            break
        result = send_request(session_id, url, text)
        print(f"\n{result['answer']}\n")


if __name__ == "__main__":
    main()
