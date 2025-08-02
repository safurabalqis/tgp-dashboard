from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func
from app.models.models import db, Crash

offense_bp = Blueprint('offense', __name__, url_prefix='/offense')

def get_primary_cause_distribution(beat=None):
    """
    Returns a list of dicts:
      [{ 'cause': <PRIM_CONTRIBUTORY_CAUSE>, 'count': <int> }, …]
    Filtered by BEAT_OF_OCCURRENCE when beat is set and != 'all'.
    """
    q = db.session.query(
            Crash.prim_contributory_cause.label('cause'),
            func.count(Crash.crash_record_id).label('count')
        )
    if beat and beat != 'all':
        # your beat column is BEAT_OF_OCCURRENCE (bigint in db)
        # region comes in as string, so we cast to int if needed
        try:
            beat_val = int(beat)
            q = q.filter(Crash.beat_of_occurrence == beat_val)
        except ValueError:
            # if someone passed a non‐int beat, you can skip the filter
            pass

    q = (q.group_by(Crash.prim_contributory_cause)
          .order_by(func.count(Crash.crash_record_id).desc())
          .limit(10)
        )

    return [
        {'cause': c or 'Unknown', 'count': cnt}
        for c, cnt in q
    ]

@offense_bp.route('/')
def offense_page():
    # pull distinct beats for the dropdown
    beats_q = (
        db.session
          .query(Crash.beat_of_occurrence)
          .distinct()
          .order_by(Crash.beat_of_occurrence)
          .all()
    )
    # flatten [(101,), (102,), …] to [101, 102, …]
    beats = [b[0] for b in beats_q if b[0] is not None]

    # initial load = all beats
    initial_data = get_primary_cause_distribution()
    labels = [row['cause'] for row in initial_data]
    values = [row['count'] for row in initial_data]

    return render_template(
        'offense.html',
        beats=beats,
        labels=labels,
        values=values
    )

@offense_bp.route('/api/primary-cause')
def offense_api():
    # client will send ?beat=101 (or 'all')
    beat = request.args.get('beat', 'all')
    data = get_primary_cause_distribution(beat)
    return jsonify(data)
