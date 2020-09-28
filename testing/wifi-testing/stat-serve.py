#!/usr/bin/python3

import http.server
import subprocess
import json

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
        comp_proc = subprocess.run('./get_stat.sh', capture_output=True)
        mac_arr = comp_proc.stdout.decode().split('\n')[:-1]
        mac_arr_json = json.dumps(mac_arr)
        s.send_html(mac_arr_json, content_type="application/json")

    def send_html(s, payload, content_type="text/html"):
        if type(payload) != bytes:
            payload = payload.encode()
        s.send_response(200)
        s.send_header("Content-Type", content_type)
        s.send_header("Content-Length", len(payload))
        s.end_headers()
        s.wfile.write(payload)

httpd = http.server.HTTPServer(server_address, MyHandler)
httpd.serve_forever()
