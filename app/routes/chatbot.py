from flask import Blueprint, request, jsonify, render_template
from chatbot.bedrock_client import get_bedrock_client
from chatbot.claude_utils import prompt_claude_v3
from chatbot.db_utils import get_schema_info
import pandas as pd, json, os, re, asyncio, time
from sqlalchemy import create_engine
import psycopg2.pool
from datetime import datetime
from botocore.exceptions import ClientError

chatbot_bp = Blueprint('chatbot', __name__)

# === Initialize AWS Bedrock client ===
client = get_bedrock_client()

# === PostgreSQL connection pool (use DATABASE_URI only) ===
DATABASE_URI = os.getenv("DATABASE_URI")

if not DATABASE_URI:
    raise RuntimeError("DATABASE_URI is not set in the environment")

pg_pool = psycopg2.pool.SimpleConnectionPool(
    1, 5, dsn=DATABASE_URI
)

def get_sqlalchemy_engine():
    """Return SQLAlchemy engine using DATABASE_URI."""
    return create_engine(DATABASE_URI)

def extract_sql_only(text: str) -> str:
    match = re.search(r"(SELECT|UPDATE|DELETE|INSERT|WITH)\s.+", text, re.IGNORECASE | re.DOTALL)
    return match.group(0).strip() if match else ""

def load_full_schema_text(path="schema.json"):
    with open(path, "r") as f:
        return json.dumps(json.load(f), indent=2)

def prompt_with_retry(user_prompt: str, retries=3, backoff=2):
    """Wrapper to call Claude with retry on ThrottlingException."""
    for attempt in range(retries):
        try:
            return prompt_claude_v3(client, user_prompt)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ThrottlingException" and attempt < retries - 1:
                wait_time = backoff * (2 ** attempt)
                print(f"⏳ Throttled by Bedrock, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except Exception as e:
            if attempt < retries - 1:
                wait_time = backoff * (2 ** attempt)
                print(f"⚠️ Error {e}, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

# === UI Route ===
@chatbot_bp.route("/chatbot", methods=["GET"])
def chatbot_ui():
    return render_template('chatbot.html')

# === API Route (RAG flow) ===
@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot_endpoint():
    user_q = request.json.get("message")

    # Ensure schema.json exists
    asyncio.run(get_schema_info(pg_pool))

    # Load full schema text
    schema_text = load_full_schema_text()

    # === Step 1: Ask Claude to generate SQL ===
    sql_prompt = f"""
You are an expert SQL assistant for a chatbot that answers traffic-related questions using PostgreSQL.

[... your existing instructions remain unchanged ...]

== FULL DATABASE SCHEMA ==
{schema_text}

Now write a valid SQL query to answer:
"{user_q}"

Only return the SQL query. No explanation.
"""

    try:
        raw_sql = prompt_with_retry(sql_prompt).strip()
        generated_sql = extract_sql_only(raw_sql)
    except Exception as e:
        return jsonify({"reply": f"❌ Claude error (SQL generation): {e}"})

    if not generated_sql:
        return jsonify({"reply": "Claude could not generate a valid SQL query."})

    if "limit" not in generated_sql.lower():
        generated_sql = generated_sql.rstrip(";") + " LIMIT 100"

    # === Step 2: Execute SQL ===
    try:
        df_result = pd.read_sql(generated_sql, get_sqlalchemy_engine())
        if df_result.empty:
            return jsonify({"reply": "I couldn't find any data matching your question. Please try asking it in a different way."})
        result_preview = df_result.head(5).to_markdown(index=False)

    except Exception as e:
        print(f"❌ SQL Execution Error: {e}")  
        return jsonify({
            "reply": "I couldn't generate a valid answer for this question yet. Try rephrasing or asking something simpler."
        })

    # === Step 3: Ask Claude to explain the result ===
    explanation_prompt = f"""
You are a traffic analyst AI.

User asked:
"{user_q}"

Here is the SQL result preview:
{result_preview}

Explain the result clearly in 2–3 sentences. Do not assume more than what the result shows. If month related instead of numbers use actual month name.
"""
    try:
        final_answer = prompt_with_retry(explanation_prompt)
    except Exception as e:
        return jsonify({"reply": f"❌ Claude error (explanation): {e}"})

    return jsonify({
        "question": user_q,
        "sql": generated_sql,
        "sql_result_preview": result_preview,
        "reply": final_answer
    })
