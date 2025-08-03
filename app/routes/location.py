# app/routes/location.py

from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import func
from main.models.models import db, Crash

location_bp = Blueprint('location', __name__, url_prefix='/location')

# Cards overview
@location_bp.route('')
def location_landing():
    # Total crashes = count of crash_record_id
    total_crashes = db.session.query(func.count(Crash.crash_record_id)).scalar()

    # Most common month
    top_month_num = (
        db.session.query(Crash.crash_month, func.count().label("count"))
        .group_by(Crash.crash_month)
        .order_by(func.count().desc())
        .first()
    )
    top_month = month_name(top_month_num[0]) if top_month_num else "N/A"

    # Most common weather (ignoring 'UNKNOWN' or null)
    top_weather = (
        db.session.query(Crash.weather_condition, func.count().label("count"))
        .filter(Crash.weather_condition.isnot(None))
        .filter(Crash.weather_condition != "UNKNOWN")
        .group_by(Crash.weather_condition)
        .order_by(func.count().desc())
        .first()
    )
    top_weather = top_weather[0] if top_weather else "N/A"

    # Most common crash type (excluding 'UNKNOWN')
    top_crash_type = (
        db.session.query(Crash.prim_contributory_cause, func.count().label("count"))
        .filter(Crash.prim_contributory_cause.isnot(None))
        .filter(Crash.prim_contributory_cause != "UNKNOWN")
        .group_by(Crash.prim_contributory_cause)
        .order_by(func.count().desc())
        .first()
    )
    top_crash_type = top_crash_type[0] if top_crash_type else "N/A"


    return render_template(
        "landing.html",
        stats={
            "total_crashes": total_crashes,
            "top_month": top_month,
            "top_weather": top_weather,
            "top_crash_type": top_crash_type,
        },
    )

def month_name(num):
    import calendar
    if num and 1 <= num <= 12:
        return calendar.month_name[num]
    return "Unknown"

# Search bar results list
@location_bp.route('/api/search')
def search_crashes():

    query = request.args.get("q", "").strip().lower()
    print(f"Received query: {query}")
    results = []

    if query:
        matched = (
            db.session.query(
                Crash.crash_record_id,
                Crash.crash_date,
                Crash.prim_contributory_cause,
                Crash.injuries_total,
                Crash.num_units,
                Crash.street_name,
            )
            .filter(Crash.street_name.ilike(f"%{query}%"))
            .order_by(Crash.crash_date.desc())
            .limit(50)
            .all()
        )

        for crash in matched:
            results.append({
                "id": crash.crash_record_id,
                "date": crash.crash_date.split("T")[0],  # assuming ISO format
                "reason": crash.prim_contributory_cause.title(),
                "injuries": crash.injuries_total,
                "vehicles": crash.num_units,
                "street": crash.street_name,
            })

    return jsonify(results)

