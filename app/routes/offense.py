# app/routes/offense.py
from flask import Blueprint, render_template, request, jsonify
from app.models import Crash
from sqlalchemy import func

bp = Blueprint('offense', __name__, url_prefix='/offense')

@bp.route('/')
def offense_page():
    # Query distinct beats for the dropdown
    beats = [b[0] for b in Crash.query.with_entities(Crash.beat_of_occurrence).distinct().all()]
    return render_template('offense.html', beats=beats)

@bp.route('/api/cause-distribution')
def api_cause_distribution():
    start = request.args.get('start_date')
    end   = request.args.get('end_date')
    region = request.args.get('region')

    q = Crash.query.filter(Crash.crash_date.between(start, end))
    if region and region != 'all':
        q = q.filter(Crash.beat_of_occurrence == region)

    data = (
        q.with_entities(Crash.prim_contributory_cause.label('cause'),
                        func.count().label('count'))
         .group_by(Crash.prim_contributory_cause)
         .order_by(func.count().desc())
         .limit(10)
         .all()
    )

    return jsonify([{'cause': c, 'count': n} for c, n in data])
