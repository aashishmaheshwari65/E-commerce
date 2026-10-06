import os
# pyrefly: ignore [missing-import]
from flask import Flask
# pyrefly: ignore [missing-import]
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing from .env")

if not SUPABASE_URL.startswith("https://"):
    raise ValueError("SUPABASE_URL must be a valid HTTP URL starting with https://. Please check your .env file.")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing from .env")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

@app.route('/')
def index():
    response = supabase.table('todos').select("*").execute()
    todos = response.data

    html = '<h1>Todos</h1><ul>'
    for todo in todos:
        html += f'<li>{todo["name"]}</li>'
    html += '</ul>'

    return html

if __name__ == '__main__':
    app.run(debug=True)
