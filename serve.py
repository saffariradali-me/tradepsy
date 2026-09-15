#!/usr/bin/env python3
"""Serve Tradepsy on localhost so it can be installed as an app.

Why this exists: browsers only offer to install a web app from a secure origin.
A file:// page is not one, so double-clicking tradepsy.html can never show an
install option no matter what the page does. http://localhost counts as secure
on every desktop browser, and this script is the smallest way to get one.

    python3 serve.py

Nothing leaves your machine. The server binds to the loopback interface only,
so it is not reachable from your network, and it serves the files in this
folder and nothing else. Stop it with Ctrl+C.
"""

import argparse
import http.server
import os
import sys
import threading
import webbrowser

PAGE = "tradepsy.html"


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map)
    # Serving the manifest as text/plain makes the browser ignore it, and the
    # install option quietly never appears.
    extensions_map[".webmanifest"] = "application/manifest+json"
    extensions_map[".json"] = "application/json"
    extensions_map[".js"] = "text/javascript"

    def send_head(self):
        # Serve the app at the bare address too. Without this, opening
        # http://localhost:8642/ lands on a directory listing, which has no
        # manifest attached and so can never be installed - an easy way to end
        # up staring at a page that looks right and is not installable.
        if self.path in ("/", "/index.html"):
            self.path = "/" + PAGE
        return super().send_head()

    def end_headers(self):
        # The service worker and the manifest must not be answered from the
        # HTTP cache, or an updated build keeps booting the previous one.
        tail = self.path.rstrip("/").rsplit("/", 1)[-1]
        if tail in ("sw.js", "manifest.webmanifest"):
            self.send_header("Cache-Control", "no-cache")
        # A service worker registered with a wider scope than its own folder is
        # rejected unless the server says otherwise. Ours does not need it, but
        # saying so costs nothing and removes one way for this to break.
        if tail == "sw.js":
            self.send_header("Service-Worker-Allowed", "/")
        super().end_headers()

    def log_message(self, fmt, *args):
        if "--verbose" in sys.argv:
            super().log_message(fmt, *args)


def open_server(port):
    """Bind the server to this exact port, or stop and explain.

    Binding for real rather than probing with a throwaway socket first. The
    probe was subtly wrong: HTTPServer sets SO_REUSEADDR and a bare socket does
    not, so a port left in TIME_WAIT by the previous run reads as busy to the
    probe and is perfectly bindable by the server a line later. Restarting
    within a minute of stopping produced a scary message about a port that was
    in fact free.

    Wandering to the next free port would be friendlier right up until it lost
    somebody's journal: the browser files saved data under the origin, and
    http://localhost:8642 and http://localhost:8643 are two different origins.
    A silent fallback would open a working app with an empty journal and no
    hint as to why.
    """
    try:
        return http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError:
        raise SystemExit(
            "\nPort %d is already in use.\n\n"
            "If Tradepsy is already running, just open http://localhost:%d/\n"
            "in your browser - that is the same app with the same saved data.\n\n"
            "If something else is using the port, close it and try again. Only\n"
            "use --port to move to another number if you have not saved anything\n"
            "yet: the browser keeps your journal per address, so a different port\n"
            "starts an empty one.\n" % (port, port)
        )


def main():
    ap = argparse.ArgumentParser(description="Serve Tradepsy on localhost.")
    ap.add_argument("--port", type=int, default=8642)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    if not os.path.exists(PAGE):
        raise SystemExit("Could not find %s next to this script." % PAGE)

    port = args.port
    server = open_server(port)
    url = "http://localhost:%d/%s" % (port, PAGE)

    print("Tradepsy is running at %s" % url)
    print("Open that address, then Settings -> Security -> Install app.")
    print("Press Ctrl+C to stop.")

    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
