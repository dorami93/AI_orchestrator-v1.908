# server.py
#
# ============================================================
# Setup: uv add openai
#        export OPENAI_API_KEY="your-api-key"
#
# Run:   python3 server.py
#        python3 server.py --model gpt-5.6-luna
#
# Exit:  > exit
# ============================================================

import argparse
from openai import OpenAI


def main(model):
    client = OpenAI()

    while True:
        text = input("> ").strip()

        if text.lower() == "exit":
            break
        if not text:
            continue

        try:
            response = client.responses.create(
                model=model,
                input=text,
            )
            print(f"\n{response.output_text}\n")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-5.6-luna")
    args = parser.parse_args()

    main(args.model)
