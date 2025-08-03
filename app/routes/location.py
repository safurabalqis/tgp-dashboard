# app/routes/location.py

from flask import Blueprint, render_template, jsonify
from app.models.models import db, Crash

location_bp = Blueprint('location', __name__, url_prefix='/location')

@location_bp.route('/')
def overview_page():
    # PASS STATS HERE
    return render_template('landing.html')

@location_bp.route('/api/heatmap')
def overview_heatmap():
    crashes = db.session.query(Crash.latitude, Crash.longitude).filter(
        Crash.latitude.isnot(None),
        Crash.longitude.isnot(None)
    ).all()

    heatmap_data = [[lat, lng] for lat, lng in crashes]
    return jsonify(heatmap_data)
