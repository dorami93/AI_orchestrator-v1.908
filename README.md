# AI Chat Dashboard

 WebブラウザをUIとして使用し、ローカルのAgentを介してCLIからAIを操作するためのシンプルなチャットUIです。

 将来的にはChatGPT・Gemini・Copilotなど複数のAIを1つの画面から操作することを想定しています。

 ## 構成

```
Browser
  │
  ▼
Web Dashboard
  │
  ▼
Local Agent
  │
  ├── ChatGPT
  ├── Gemini
  └── Copilot
```

 Web側ではAIサービスを直接操作せず、Local Agentにリクエストを送ります。

 ## ファイル構成

```
.
├── index.html
├── style.css
├── main.py
├── call_cli_llm.py
└── output.py
```

 - `index.html` — Web UIとPyodideの起動
- `style.css` — UI
- `main.py` — チャット処理
- `call_cli_llm.py` — Local Agentとの通信
- `output.py` — Markdown表示

 ## 動作

```
ユーザー
   ↓
index.html
   ↓
Pyodide
   ↓
main.py
   ↓
call_cli_llm.py
   ↓
Local Agent
```

 Local AgentのAPIは以下を想定しています。

```
POST http://127.0.0.1:8000/ask
```

 リクエスト:

```
{
  "messages": [
    {
      "role": "user",
      "content": "こんにちは"
    }
  ]
}
```

 レスポンス:

```
{
  "content": "こんにちは！"
}
```

 ## 必要なもの

 - Python
- Pyodide
- Local Agent
- ブラウザ

 Markdownの表示には `marked.js` を使用しています。

 ## 実行

 Webサーバー経由で `index.html` を開きます。

```
python -m http.server 8080
```

 その後、ブラウザで以下を開きます。

```
http://localhost:8080
```

 別途Local Agentを起動して、

```
http://127.0.0.1:8000/ask
```

 でリクエストを受けられる状態にします。

 ## 目的

 このプロジェクトでは、Electronのような専用ブラウザを作るのではなく、

 **WebサイトをUIとして利用し、ローカルAgentがAIサービスを操作する**

 という構成を目指しています。

 将来的には、

 - ChatGPT / Gemini / Copilotの同時実行
- AIごとの回答比較
- AI同士の会話
- CLIからの操作
- 複数AIを組み合わせたワークフロー

 などへの拡張を想定しています。

 ## Status

 🚧 開発中
