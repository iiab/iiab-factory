import http.server
import subprocess

PORT = 10080
server_address = ('', PORT)

#Handler = http.server.SimpleHTTPRequestHandler

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(s):
        html = ''
        if s.path == '/test':
            s.test_resp()
        else:
            s.get_wifi_stat()

    def test_resp(s):
        html = "<html><head><title>Title goes here.</title></head>"
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

Handler = MyHandler
httpd = http.server.HTTPServer(server_address, Handler)
httpd.serve_forever()
