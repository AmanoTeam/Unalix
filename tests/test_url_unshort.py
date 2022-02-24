import asyncio
import http.server
import _thread as thread

import unalix

hostname = "127.0.0.1"
port = 56885

base_url = f"http://{hostname}:{port}"

class Server(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/ok":
            self.send_response(200)
        elif self.path == "/redirect-to-tracking":
            self.send_response(301)
            self.send_header("Location", f"http://{hostname}:{port}/ok?utm_source=127.0.0.1")
        elif self.path == "/absolute-redirect":
            self.send_response(301)
            self.send_header("Location", f"http://{hostname}:{port}/redirect-to-tracking")
        elif self.path == "/relative-redirect":
            self.send_response(301)
            self.send_header("Location", "ok")
        elif self.path == "/root-redirect":
            self.send_response(301)
            self.send_header("Location", "/redirect-to-tracking")
        elif self.path == "/i-dont-know-its-name-redirect":
            self.send_response(301)
            self.send_header("Location", f"//{hostname}:{port}/redirect-to-tracking")

        self.end_headers()

server = http.server.HTTPServer((hostname, port), Server)

thread.start_new_thread(server.serve_forever, ())

def test_unshort():

    event_policy = asyncio.get_event_loop_policy()
    event_loop = event_policy.new_event_loop()

    unmodified_url = f"{base_url}/absolute-redirect"

    assert unalix.unshort_url(unmodified_url) == f"{base_url}/ok"
    assert event_loop.run_until_complete(unalix.aunshort_url(unmodified_url)) == f"{base_url}/ok"

    unmodified_url = f"{base_url}/relative-redirect"

    assert unalix.unshort_url(unmodified_url) == f"{base_url}/ok"
    assert event_loop.run_until_complete(unalix.aunshort_url(unmodified_url)) == f"{base_url}/ok"

    unmodified_url = f"{base_url}/root-redirect"

    assert unalix.unshort_url(unmodified_url) == f"{base_url}/ok"
    assert event_loop.run_until_complete(unalix.aunshort_url(unmodified_url)) == f"{base_url}/ok"    

    unmodified_url = f"{base_url}/i-dont-know-its-name-redirect"

    assert unalix.unshort_url(unmodified_url) == f"{base_url}/ok"
    assert event_loop.run_until_complete(unalix.aunshort_url(unmodified_url)) == f"{base_url}/ok"

    server.server_close()

