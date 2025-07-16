import http.server
import socketserver
import urllib.parse
import json
import os
import cgi

PORT = 8888

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/chat':
            length = int(self.headers.get('Content-Length'))
            data = self.rfile.read(length).decode('utf-8')
            params = urllib.parse.parse_qs(data)
            message = params.get('message', [''])[0]
            response = f"You said: {message}"
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response}).encode())
        elif self.path == '/upload':
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            if ctype == 'multipart/form-data':
                form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                        environ={'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': self.headers.get('Content-Type')})
                if 'file' in form:
                    fileitem = form['file']
                    if fileitem.filename:
                        fname = os.path.basename(fileitem.filename)
                        os.makedirs('uploads', exist_ok=True)
                        with open(os.path.join('uploads', fname), 'wb') as f:
                            f.write(fileitem.file.read())
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(404)

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f"Serving on http://localhost:{PORT}")
    httpd.serve_forever()
