# app/routes/offense.py

from flask import Blueprint, render_template, request, jsonify, current_app
from sqlalchemy import func
from app.models.models import db, Crash
import os

offense_bp = Blueprint('offense', __name__, url_prefix='/offense')

def get_primary_cause_distribution(beat='all'):
    """
    Returns a list of dicts:
      [{ 'cause': <PRIM_CONTRIBUTORY_CAUSE>, 'count': <int> }, …]
    filtered by beat_of_occurrence when beat!='all'.
    """
    q = db.session.query(
        Crash.prim_contributory_cause.label('cause'),
        func.count(Crash.crash_record_id).label('count')
    )
    if beat != 'all':
        try:
            b = int(beat)
            q = q.filter(Crash.beat_of_occurrence == b)
        except ValueError:
            pass

    q = (q
         .group_by(Crash.prim_contributory_cause)
         .order_by(func.count(Crash.crash_record_id).desc())
         .limit(10)
    )

    return [
        {'cause': c or 'Unknown', 'count': cnt}
        for c, cnt in q
    ]

def get_hit_and_run_features(beat='all'):
    """
    Returns a list of GeoJSON Feature dicts for hit-and-run crashes,
    filtered by beat_of_occurrence if beat!='all'.
    """
    q = db.session.query(
        Crash.latitude.label('lat'),
        Crash.longitude.label('lng'),
        Crash.crash_date.label('date'),
        Crash.prim_contributory_cause.label('cause')
    ).filter(Crash.hit_and_run_i == 'Y')

    if beat != 'all':
        try:
            b = int(beat)
            q = q.filter(Crash.beat_of_occurrence == b)
        except ValueError:
            pass

    features = []
    for row in q:
        features.append({
            "type": "Feature",
            "properties": {
                "date": row.date,
                "cause": row.cause or 'Unknown'
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row.lng, row.lat]
            }
        })
    return features

@offense_bp.route('/')
def offense_page():
    # distinct beats for dropdown
    beats_q = (
        db.session.query(Crash.beat_of_occurrence)
        .distinct()
        .order_by(Crash.beat_of_occurrence)
        .all()
    )
    beats = [b[0] for b in beats_q if b[0] is not None]

    # initial chart data (all beats)
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
def primary_cause_api():
    beat = request.args.get('beat', 'all')
    data = get_primary_cause_distribution(beat)
    return jsonify(data)

@offense_bp.route('/api/hit-and-run')
def hit_and_run_api():
    beat = request.args.get('beat', 'all')
    features = get_hit_and_run_features(beat)
    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })

@offense_bp.route('/api/beat-choropleth')
def beat_choropleth_api():
    # 1) Count hit-and-run per beat
    rows = db.session.query(
        Crash.beat_of_occurrence.label('beat'),
        func.count(Crash.crash_record_id).label('count')
    ).filter(Crash.hit_and_run_i=='Y').group_by(Crash.beat_of_occurrence).all()
    counts = {b: c for b, c in rows}

    # 2) Load static GeoJSON
    geo_path = os.path.join(current_app.root_path, 'static', 'data', 'beat_polygons.geojson')
    with open(geo_path) as f:
        geo = json.load(f)

    # 3) Annotate properties
    for feat in geo['features']:
        beat_id = feat['properties'].get('beat_id')
        feat['properties']['hit_and_run_count'] = counts.get(int(beat_id), 0)

    return jsonify(geo)