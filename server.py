# server.py
# ====== Usage ======
# python server.py
# http://127.0.0.1:8000/

from http.server import BaseHTTPRequestHandler, HTTPServer

def handshake():
    return '{"status":"ok"}'

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(handshake().encode())

def main():
    HTTPServer(("127.0.0.1", 8000), Server).serve_forever()

if __name__ == "__main__":
    main()
