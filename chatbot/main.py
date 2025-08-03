from fastapi import FastAPI
from pydantic import BaseModel
from chatbot.bedrock_client import get_bedrock_client
from chatbot.claude_utils import prompt_claude_v3
from chatbot.db_utils import get_schema_info
import pandas as pd
import json
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import re
import psycopg2.pool
import asyncio

load_dotenv()
app = FastAPI()
client = get_bedrock_client()

# 🔧 PostgreSQL connection pool
pg_pool = psycopg2.pool.SimpleConnectionPool(
    1, 5,
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=os.getenv("DB_PORT", 5432)
)

# 💡 Request structure
class AskRequest(BaseModel):
    question: str


# 💡 Get SQLAlchemy engine
def get_sqlalchemy_engine():
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(db_url)


# 💡 Extract SQL only
def extract_sql_only(text: str) -> str:
    match = re.search(r"(SELECT|UPDATE|DELETE|INSERT|WITH)\s.+", text, re.IGNORECASE | re.DOTALL)
    return match.group(0).strip() if match else ""


# 💡 Load full schema.json as string
def load_full_schema_text(path="schema.json"):
    with open(path, "r") as f:
        return json.dumps(json.load(f), indent=2)


# 🚀 Main endpoint
@app.post("/ask")
def ask_data(request: AskRequest):
    user_q = request.question

    # 🔹 Ensure schema.json exists (auto-generate if missing)
    asyncio.run(get_schema_info(pg_pool))

    # 🔹 Load full schema for prompt
    full_schema_json_text = load_full_schema_text()

    # 🔹 Step 1: Ask Claude to generate SQL
    sql_prompt = f"""
You are an expert SQL assistant for a chatbot that answers traffic-related questions using PostgreSQL.

IMPORTANT RULES:
- Wrap all column names in double quotes.
- Use EXTRACT(YEAR FROM "CRASH_DATE") = 2023 when filtering by year.
- Do not include explanations or markdown. Only return a valid SQL query starting with SELECT or WITH.
- When referring to column "LIGHTING_CONDITION" the possible values include "DAWN", "DARKNESS", "DAYLIGHT", "DUSK",  "UNKNOWN", "DARKNESS, LIGHTED ROAD".
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
{full_schema_json_text}

Now write a valid SQL query to answer:
"{user_q}"

Only return the SQL query. No explanation.
"""

    try:
        raw_sql = prompt_claude_v3(client, sql_prompt).strip()
        generated_sql = extract_sql_only(raw_sql)
        print(f"💡 Claude Raw:\n{raw_sql}")
        print(f"✅ SQL:\n{generated_sql}")
    except Exception as e:
        return {"error": "Claude failed to generate SQL", "details": str(e)}

    if not generated_sql:
        return {"question": user_q, "answer": "Claude could not generate a valid SQL query."}

    if "limit" not in generated_sql.lower():
        generated_sql = generated_sql.rstrip().rstrip(";") + " LIMIT 100"


    try:
        df_result = pd.read_sql(generated_sql, get_sqlalchemy_engine())
        if df_result.empty:
            return {"question": user_q, "sql": generated_sql, "answer": "No matching data found in the database."}
        result_preview = df_result.head(5).to_markdown(index=False)
    except Exception as e:
        return {"error": "Failed to execute SQL", "sql": generated_sql, "details": str(e)}

    # 🔹 Step 3: Ask Claude to explain the result
    explanation_prompt = f"""
You are a traffic analyst AI.

User asked:
"{user_q}"

Here is the SQL result preview:
{result_preview}

Explain the result clearly in 2–3 sentences. Do not assume more than what the result shows.
"""

    try:
        final_answer = prompt_claude_v3(client, explanation_prompt)
    except Exception as e:
        return {"error": "Claude failed to explain result", "details": str(e)}

    return {
        "question": user_q,
        "sql": generated_sql,
        "sql_result_preview": result_preview,
        "answer": final_answer
    }
