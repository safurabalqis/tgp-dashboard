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

IMPORTANT RULES:
- If greeted by the user, respond normally and naturally without generating SQL.
- If the user input is not SQL-related, reply concisely in plain language without generating SQL.
- Always return only one SQL query per request; if multiple steps are needed, use a single WITH statement.
- If the user’s question is vague or incomplete, ask for clarification instead of assuming their intent.
- Always use lowercase, snake_case aliases for derived columns (e.g., crash_count, crash_month).
- Include NULL checks for columns that may have missing data when filtering categories.
- If the user asks for a value outside the allowed categories for any column, ask them to use the correct values.
- When the user requests "top N" results, use LIMIT appropriately.
- Format SQL with proper indentation for readability.
- Wrap all column names in double quotes.
- Convert "CRASH_DATE" from text to a proper timestamp using 
  TO_TIMESTAMP("CRASH_DATE", 'MM/DD/YYYY HH12:MI:SS AM').
- Use EXISTS or JOIN when linking tables rather than subqueries if possible.

ADDITIONAL RULES:
- Use EXTRACT(YEAR FROM "CRASH_DATE") = 2024 when filtering by year.
- Do not include explanations or markdown. Only return a valid SQL query starting with SELECT or WITH.
- When referring to column "LIGHTING_CONDITION" the possible values include "DAWN", "DARKNESS", "DAYLIGHT", "DUSK", "UNKNOWN", "DARKNESS, LIGHTED ROAD".
- When referring to the column "WEATHER_CONDITION", the possible values include "SEVERE CROSS WIND GATE", "OTHER", "UNKNOWN", "FREEZING RAIN/DRIZZLE", "SLEET/HAIL", "CLOUDY/OVERCAST", "BLOWING SNOW", "SNOW", "FOG/SMOKE/HAZE", "CLEAR", "BLOWING SAND, SOIL, DIRT", and "RAIN".
- When referring to the column "TRAFFIC_CONTROL_DEVICE", the possible values include "YIELD", "FLASHING CONTROL SIGNAL", "DELINEATORS", "BICYCLE CROSSING SIGN", "POLICE/FLAGMAN", "OTHER REG. SIGN", "RR CROSSING SIGN", "OTHER RAILROAD CROSSING", "PEDESTRIAN CROSSING SIGN", "OTHER", "TRAFFIC SIGNAL", "NO CONTROLS", "NO PASSING", "RAILROAD CROSSING GATE", "OTHER WARNING SIGN", "STOP SIGN/FLASHER", "UNKNOWN", and "SCHOOL ZONE".
- When referring to the column "DEVICE_CONDITION", the possible values include "NOT FUNCTIONING", "FUNCTIONING IMPROPERLY", "FUNCTIONING PROPERLY", "OTHER", "UNKNOWN", "MISSING", "WORN REFLECTIVE MATERIAL", and "NO CONTROLS".
- When referring to the column "FIRST_CRASH_TYPE", the possible values include "PEDESTRIAN", "REAR END", "SIDESWIPE OPPOSITE DIRECTION", "ANIMAL", "OTHER OBJECT", "TRAIN", "PARKED MOTOR VEHICLE", "HEAD ON", "TURNING", "SIDESWIPE SAME DIRECTION", "OTHER NONCOLLISION", "REAR TO SIDE", "FIXED OBJECT", "REAR TO REAR", "REAR TO FRONT", "PEDALCYCLIST", "OVERTURNED", and "ANGLE".
- When referring to the column "TRAFFICWAY_TYPE", the possible values include "CENTER TURN LANE", "FIVE POINT, OR MORE", "NOT DIVIDED", "PARKING LOT", "NOT REPORTED", "DRIVEWAY", "RAMP", "DIVIDED - W/MEDIAN (NOT RAISED)", "ALLEY", "UNKNOWN INTERSECTION TYPE", "OTHER", "ONE-WAY", "T-INTERSECTION", "FOUR WAY", "L-INTERSECTION", "Y-INTERSECTION", "TRAFFIC ROUTE", "UNKNOWN", "DIVIDED - W/MEDIAN BARRIER", and "ROUNDABOUT".
- When referring to the column "ALIGNMENT", the possible values include "CURVE ON GRADE", "STRAIGHT ON HILLCREST", "STRAIGHT AND LEVEL", "CURVE ON HILLCREST", "CURVE, LEVEL", and "STRAIGHT ON GRADE".
- When referring to the column "ROADWAY_SURFACE_COND", the possible values include "SNOW OR SLUSH", "OTHER", "UNKNOWN", "SAND, MUD, DIRT", "DRY", "ICE", and "WET".
- When referring to the column "ROAD_DEFECT", the possible values include "SHOULDER DEFECT", "WORN SURFACE", "OTHER", "UNKNOWN", "NO DEFECTS", "DEBRIS ON ROADWAY", and "RUT, HOLES".
- When referring to the column "CRASH_TYPE", the possible values include "NO INJURY / DRIVE AWAY" and "INJURY AND / OR TOW DUE TO CRASH".


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
