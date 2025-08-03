# app/routes/location.py

from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import func
from app.models.models import db, Crash
import calendar

location_bp = Blueprint("location", __name__, url_prefix="/location")

# --------------------------------
# Landing Summary Cards
# --------------------------------
@location_bp.route("")
def location_landing():
    total_crashes = db.session.query(func.count(Crash.crash_record_id)).scalar()

    top_month_num = (
        db.session.query(Crash.crash_month, func.count().label("count"))
        .group_by(Crash.crash_month)
        .order_by(func.count().desc())
        .first()
    )
    top_month = month_name(top_month_num[0]) if top_month_num else "N/A"

    top_weather = (
        db.session.query(Crash.weather_condition, func.count().label("count"))
        .filter(Crash.weather_condition.isnot(None))
        .filter(Crash.weather_condition != "UNKNOWN")
        .group_by(Crash.weather_condition)
        .order_by(func.count().desc())
        .first()
    )
    top_weather = top_weather[0] if top_weather else "N/A"

    top_crash_type = (
        db.session.query(Crash.prim_contributory_cause, func.count().label("count"))
        .filter(Crash.prim_contributory_cause.isnot(None))
        .filter(Crash.prim_contributory_cause != "UNABLE TO DETERMINE")
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
    if num and 1 <= num <= 12:
        return calendar.month_name[num]
    else: return "Unknown"

# --------------------------------
# Street search
# --------------------------------
@location_bp.route("/api/streets")
def search_streets():
    query = request.args.get("q", "").lower()
    metric = request.args.get("metric", "crashes")

    if not query:
        return jsonify([])

    # Determine which metric to sum
    if metric == "injuries":
        value_column = func.sum(Crash.injuries_total).label("value")
    elif metric == "vehicles":
        value_column = func.sum(Crash.num_units).label("value")
    else:
        value_column = func.count().label("value")

    streets = (
        db.session.query(
            Crash.street_name,
            func.avg(Crash.latitude).label("lat"),
            func.avg(Crash.longitude).label("lng"),
            value_column
        )
        .filter(Crash.street_name.ilike(f"%{query}%"))
        .filter(Crash.latitude.isnot(None), Crash.longitude.isnot(None))
        .group_by(Crash.street_name)
        .order_by(value_column.desc())
        .limit(10)
        .all()
    )

    result = [
        {
            "name": name.title(),
            "coords": [lat, lng],
            "crash_count": int(value)
        }
        for name, lat, lng, value in streets if lat and lng
    ]

    return jsonify(result)