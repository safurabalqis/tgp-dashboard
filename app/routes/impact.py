from flask import Blueprint, render_template, jsonify, request
from main.models.models import db, Crash
from datetime import datetime


impact_bp = Blueprint('impact', __name__)

@impact_bp.route('/impact')
def impact():
    selected_crash_type = request.args.get('crash_type', 'All')

    query = db.session.query(Crash)
    if selected_crash_type != "All":
        query = query.filter(Crash.crash_type == selected_crash_type)

    crash_data = (
        db.session.query(Crash.crash_type, db.func.count(Crash.crash_record_id))
        .group_by(Crash.crash_type)
        .order_by(db.func.count(Crash.crash_record_id).desc())
        .all()
    )
    labels = [row[0] if row[0] else 'Unknown' for row in crash_data]
    values = [row[1] for row in crash_data]

    hour_data = (
        query
        .with_entities(Crash.crash_hour, db.func.count(Crash.crash_record_id))
        .group_by(Crash.crash_hour)
        .order_by(Crash.crash_hour)
        .all()
    )
    hour_labels = [row[0] for row in hour_data]
    hour_counts = [row[1] for row in hour_data]

    # ✅ Extra hour-based stats (shown only when filtered)
    hour_insights = None
    if selected_crash_type != "All" and hour_data:
        zipped = list(zip(hour_labels, hour_counts))
        sorted_hours = sorted(zipped, key=lambda x: x[1], reverse=True)
        most_frequent_hour = sorted_hours[0][0]
        top_hours = [str(hour) for hour, _ in sorted_hours[:3]]
        avg_crash_hour = round(sum(hour_counts) / len(hour_counts), 1) if hour_counts else 0

        hour_insights = {
            "most_frequent_hour": most_frequent_hour,
            "avg_crash_hour": avg_crash_hour,
            "top_hours": top_hours
        }

    injury_data = (
        query
        .with_entities(Crash.most_severe_injury, db.func.count(Crash.crash_record_id))
        .group_by(Crash.most_severe_injury)
        .order_by(db.func.count(Crash.crash_record_id).desc())
        .all()
    )
    injury_labels = [row[0] if row[0] else 'Unknown' for row in injury_data]
    injury_values = [row[1] for row in injury_data]
    injury_breakdown = dict(zip(injury_labels, injury_values))

    crash_type_options = sorted(set(row[0] for row in db.session.query(Crash.crash_type).distinct() if row[0]))

    total_crashes = query.count()
    total_injuries = sum(injury_values)

    
    return render_template(
        'impact.html',
        labels=labels,
        values=values,
        hour_labels=hour_labels,
        hour_counts=hour_counts,
        injury_labels=injury_labels,
        injury_values=injury_values,
        injury_breakdown=injury_breakdown,
        selected_crash_type=selected_crash_type,
        crash_type_options=crash_type_options,
        total_crashes=total_crashes,
        total_injuries=total_injuries,
        hour_insights=hour_insights,
       
    )


# ✅ JSON API route for filtered injury stats
@impact_bp.route('/api/filter/<crash_type>')
def filter_crash(crash_type):
    query = db.session.query(Crash).filter(Crash.crash_type == crash_type) if crash_type != "All" else db.session.query(Crash)

    injury_data = (
        query.with_entities(Crash.most_severe_injury, db.func.count(Crash.crash_record_id))
        .group_by(Crash.most_severe_injury)
        .order_by(db.func.count(Crash.crash_record_id).desc())
        .all()
    )
    injury_labels = [row[0] if row[0] else 'Unknown' for row in injury_data]
    injury_values = [row[1] for row in injury_data]
    injury_map = dict(zip(injury_labels, injury_values))

    return jsonify({
        "injury_labels": injury_labels,
        "injury_values": injury_values,
        "injury_map": injury_map
    })
