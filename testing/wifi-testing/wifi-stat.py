#!/usr/bin/python3

import http.server
import subprocess

PORT = 10080
server_address = ('', PORT)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(s):
        if s.path == '/test':
            s.test_resp()
        elif s.path == '/stat':
            s.get_wifi_stat()
        else:
            super().do_GET()

    def test_resp(s):
        html = "<html><head><title>Test Page.</title></head>"
        html += "<body><p>This is a test.</p>"
        html += "<p>You accessed path: %s</p>" % s.path
        html += "</body></html>"
        s.send_html(html)

    def get_wifi_stat(s):
        comp_proc = subprocess.run('./get_sta.sh', capture_output=True)
        html = '<html><body>'
        html += comp_proc.stdout.decode()
        html += '</body></html>'
        s.send_html(html)

    def send_html(s, html):
        if type(html) != bytes:
            html = html.encode()
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write(html)

httpd = http.server.HTTPServer(server_address, MyHandler)
httpd.serve_forever()
