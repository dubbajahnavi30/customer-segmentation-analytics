"""
Nexus RFM Web Application Launcher
Starts local Python HTTP server and automatically opens http://localhost:8000 in your default browser.
"""

import os
import sys
import webbrowser
import http.server
import socketserver

PORT = 8000
DIRECTORY = os.path.abspath(os.path.dirname(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    print("=" * 70)
    print(" NEXUS RFM & CLUSTERING ANALYTICS PLATFORM")
    print("=" * 70)
    print(f" Serving dashboard from: {DIRECTORY}")
    print(f" Dashboard URL:          http://localhost:{PORT}")
    print(" Opening your default web browser...")
    print(" Press Ctrl+C in this terminal to stop the server.")
    print("=" * 70)

    webbrowser.open(f"http://localhost:{PORT}")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down dashboard server. Goodbye!")

if __name__ == "__main__":
    main()
