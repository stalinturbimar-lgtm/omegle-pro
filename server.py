from http.server import BaseHTTPRequestHandler, HTTPServer
import json, uuid

PORT = 8000
users = {}
waiting = None

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())

        elif self.path.startswith("/poll"):
            uid = self.headers.get("User-ID")
            msgs = users.get(uid, {}).get("queue", [])
            users[uid]["queue"] = []
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(msgs).encode())

    def do_POST(self):
        global waiting
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/connect":
            uid = str(uuid.uuid4())
            users[uid] = {"partner": None, "queue": []}

            if waiting and waiting in users:
                users[uid]["partner"] = waiting
                users[waiting]["partner"] = uid
                waiting = None
            else:
                waiting = uid

            self.send_response(200)
            self.end_headers()
            self.wfile.write(uid.encode())

        elif self.path == "/signal":
            uid = self.headers.get("User-ID")
            partner = users.get(uid, {}).get("partner")
            if partner in users:
                users[partner]["queue"].append(data)

            self.send_response(200)
            self.end_headers()

def run():
    print(f"Servidor en http://localhost:{PORT}")
    HTTPServer(("", PORT), Handler).serve_forever()

run()
