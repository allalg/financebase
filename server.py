"""
FinanceBase - Local development server
Uses official Groq Python library.

First time setup — run this once:
    pip install groq

Get your free API key at: https://console.groq.com
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    from groq import Groq
except ImportError:
    print("\n  ERROR: 'groq' library not installed!")
    print("  Run this once:  pip install groq")
    print("  Then restart the server.\n")
    exit(1)

def _load_dotenv_key(base_dir):
    """Read GROQ_API_KEY from a local .env file without extra dependencies."""
    env_path = os.path.join(base_dir, ".env")
    if not os.path.exists(env_path):
        return ""

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip().lstrip("\ufeff")
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                normalized_key = key.strip().removeprefix("export ").removeprefix("set ")
                if normalized_key == "GROQ_API_KEY":
                    # Support inline comments: GROQ_API_KEY=... # comment
                    cleaned = value.split("#", 1)[0].strip().strip('"').strip("'")
                    return cleaned
    except (OSError, UnicodeDecodeError):
        return ""

    return ""


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Priority: shell environment variable, then local .env file.
# PowerShell example: $env:GROQ_API_KEY="gsk_your_key_here"
API_KEY = os.environ.get("GROQ_API_KEY", "").strip() or _load_dotenv_key(BASE_DIR)

PORT = int(os.environ.get("PORT", 8080))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are FinanceBase Tutor — a warm, encouraging finance teacher for students aged 15-22.

RULES:
- Always explain like you're talking to someone who has NEVER studied finance
- Use relatable analogies (e.g. compare a balance sheet to a household budget)
- Keep responses concise — 3 to 6 short paragraphs max unless asked for more
- Use simple bullet points when listing things
- Bold key terms using **term** markdown (which will be rendered)
- Add a 1-sentence Quick Summary at the end of every answer
- Never use complex jargon without immediately explaining it
- Be warm, friendly, and encouraging

FORMAT your response:
- Use **bold** for key terms
- Use line breaks between paragraphs
- End with: Quick Summary: [one sentence]"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  {args[0]} {args[1]}")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            filepath = os.path.join(BASE_DIR, "index.html")
            if not os.path.exists(filepath):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"index.html not found - make sure it's in the same folder as server.py")
                return
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path != "/chat":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            self._json_response(400, {"error": "Request body is empty."})
            return

        try:
            body = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self._json_response(400, {"error": "Invalid JSON body."})
            return

        messages = body.get("messages", [])
        if not isinstance(messages, list):
            self._json_response(400, {"error": "'messages' must be a list."})
            return

        if not API_KEY:
            print("  ERROR: GROQ_API_KEY is not set in environment.")
            self._json_response(500, {"error": "API key not set. Set GROQ_API_KEY in your shell and restart server.py."})
            return

        print(f"  Key: {API_KEY[:8]}...  Model: {MODEL}")

        try:
            client = Groq(api_key=API_KEY)

            completion = client.chat.completions.create(
                model=MODEL,
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + messages
            )

            reply = completion.choices[0].message.content
            print("  Groq responded OK")
            self._json_response(200, {"reply": reply})

        except Exception as e:
            err = str(e)
            print(f"  Error: {err}")

            # Groq code 1010 commonly means key/account access issue.
            if "error code: 1010" in err.lower():
                self._json_response(502, {"error": "Groq rejected the request (code 1010). Check that GROQ_API_KEY is valid/active and has API access."})
                return

            self._json_response(500, {"error": err})

    def _json_response(self, status, data):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


if __name__ == "__main__":
    print("\n" + "="*50)
    if not API_KEY:
        print("  ERROR: No API key found!")
        print("  Set GROQ_API_KEY in your shell before running this server")
        print("  Get a free key at https://console.groq.com")
    else:
        print(f"  API key loaded: {API_KEY[:8]}...")
        print(f"  Model: {MODEL}")
    print("="*50)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"  Server live on 0.0.0.0:{PORT}")
    print("  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Goodbye!")