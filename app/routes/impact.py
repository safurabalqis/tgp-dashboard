from flask import Blueprint, render_template
from app.models.models import db, Crash

impact_bp = Blueprint('impact', __name__)

@impact_bp.route('/impact')
def impact():
    # -- Bar chart: Crash type
    crash_data = (
        db.session.query(Crash.crash_type, db.func.count(Crash.crash_record_id))
        .group_by(Crash.crash_type)
        .order_by(db.func.count(Crash.crash_record_id).desc())
        .all()
    )
    labels = [row[0] if row[0] else 'Unknown' for row in crash_data]
    values = [row[1] for row in crash_data]

    # -- Line chart: Crashes per hour
    hour_data = (
        db.session.query(Crash.crash_hour, db.func.count(Crash.crash_record_id))
        .group_by(Crash.crash_hour)
        .order_by(Crash.crash_hour)
        .all()
    )
    hour_labels = [row[0] for row in hour_data]
    hour_counts = [row[1] for row in hour_data]

   # -- Pie Chart: Most Severe Injury
    injury_data = (
        db.session.query(Crash.most_severe_injury, db.func.count(Crash.crash_record_id))
        .group_by(Crash.most_severe_injury)
        .order_by(db.func.count(Crash.crash_record_id).desc())
        .all()
    )

    injury_labels = [row[0] if row[0] else 'Unknown' for row in injury_data]
    injury_values = [row[1] for row in injury_data]

    return render_template(
        'impact.html',
        labels=labels,
        values=values,
        hour_labels=hour_labels,
        hour_counts=hour_counts,
        injury_labels=injury_labels,
        injury_values=injury_values
    )
