import http.server
import socketserver
import urllib.parse
import json
import os
import cgi

PORT = 8888

# Global state for conversation and uploaded file
history = []
uploaded_file = None


def orchestrate(question, file_path):
    """Very simple analysis of an uploaded CSV file."""
    if not file_path or not os.path.exists(file_path):
        return "No file uploaded to analyze."
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            line_count = sum(1 for _ in f)
        return f"File '{os.path.basename(file_path)}' has {line_count} lines."
    except Exception as exc:
        return f"Error reading file: {exc}"


def chat_with_model(history_list):
    """Dummy chat model that echoes the last user message."""
    last_user = history_list[-1]["content"] if history_list else ""
    return f"Echo: {last_user}"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        global uploaded_file
        if self.path == "/chat":
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length).decode("utf-8")
            params = urllib.parse.parse_qs(data)
            message = params.get("message", [""])[0]
            mode = params.get("mode", ["chat"])[0]

            history.append({"role": "user", "content": message})
            if mode.lower() == "analyze":
                reply = orchestrate(message, uploaded_file)
            else:
                reply = chat_with_model(history)
            history.append({"role": "assistant", "content": reply})

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"response": reply}).encode())
        elif self.path == "/upload":
            ctype, pdict = cgi.parse_header(self.headers.get("Content-Type"))
            if ctype == "multipart/form-data":
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        "REQUEST_METHOD": "POST",
                        "CONTENT_TYPE": self.headers.get("Content-Type"),
                    },
                )
                if "file" in form:
                    fileitem = form["file"]
                    if fileitem.filename:
                        fname = os.path.basename(fileitem.filename)
                        os.makedirs("uploads", exist_ok=True)
                        path = os.path.join("uploads", fname)
                        with open(path, "wb") as f:
                            f.write(fileitem.file.read())
                        uploaded_file = path
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on http://localhost:{PORT}")
    httpd.serve_forever()
