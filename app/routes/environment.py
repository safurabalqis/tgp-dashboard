from flask import Blueprint, render_template, jsonify, request
from app.models.models import db, Crash
import folium
from folium.plugins import HeatMap
import os

# Blueprint
environment_bp = Blueprint('environment', __name__, url_prefix='/environment')

# === Main Page ===
@environment_bp.route('/')
def environment_page():
    return render_template('environment.html')

# === Filters Endpoint (load once) ===
@environment_bp.route('/api/filters', methods=['GET'])
def environment_filters():
    """Return unique filter options for dropdowns"""
    weather = [row[0] for row in db.session.query(Crash.weather_condition).distinct()]
    speed = [row[0] for row in db.session.query(Crash.posted_speed_limit).distinct()]
    lighting = [row[0] for row in db.session.query(Crash.lighting_condition).distinct()]

    return jsonify({
        "weather": sorted([w for w in weather if w]),
        "speed": sorted([s for s in speed if s]),
        "lighting": sorted([l for l in lighting if l])
    })

# === Metrics + Charts Endpoint ===
@environment_bp.route('/api/data', methods=['GET'])
def environment_data():
    month = request.args.get('month', 'All')
    weather = request.args.get('weather', 'All')
    speed = request.args.get('speed', 'All')
    lighting = request.args.get('lighting', 'All')

    query = Crash.query

    # Apply filters
    if month != 'All':
        query = query.filter(Crash.crash_month == int(month))
    if weather != 'All':
        query = query.filter(Crash.weather_condition == weather)
    if speed != 'All':
        query = query.filter(Crash.posted_speed_limit == int(speed))
    if lighting != 'All':
        query = query.filter(Crash.lighting_condition == lighting)

    crashes = query.with_entities(
        Crash.street_name,
        Crash.injuries_fatal,
        Crash.injuries_incapacitating,
        Crash.posted_speed_limit,
        Crash.weather_condition,
        Crash.lighting_condition
    ).all()

    if not crashes:
        return jsonify({
            "metrics": {
                "total": 0,
                "common_street": "-",
                "common_street_count": 0,
                "severe": 0
            },
            "charts": {
                "speed": [],
                "weather": [],
                "lighting": []
            }
        })

    # Metrics
    total_crashes = len(crashes)

    # Most common street
    street_counts = {}
    for c in crashes:
        if c.street_name:
            street_counts[c.street_name] = street_counts.get(c.street_name, 0) + 1
    common_street, street_count = ("-", 0)
    if street_counts:
        common_street, street_count = max(street_counts.items(), key=lambda x: x[1])

    severe_count = sum(
        1 for c in crashes if (c.injuries_fatal and c.injuries_fatal > 0) or
                              (c.injuries_incapacitating and c.injuries_incapacitating > 0)
    )

    # Charts
    speed_counts = {}
    weather_counts = {}
    lighting_counts = {}

    for c in crashes:
        speed_counts[c.posted_speed_limit] = speed_counts.get(c.posted_speed_limit, 0) + 1
        weather_counts[c.weather_condition] = weather_counts.get(c.weather_condition, 0) + 1
        lighting_counts[c.lighting_condition] = lighting_counts.get(c.lighting_condition, 0) + 1

    return jsonify({
        "metrics": {
            "total": total_crashes,
            "common_street": common_street,
            "common_street_count": street_count,
            "severe": severe_count
        },
        "charts": {
            "speed": [{"label": str(k), "count": v} for k, v in speed_counts.items()],
            "weather": [{"label": k, "count": v} for k, v in weather_counts.items()],
            "lighting": [{"label": k, "count": v} for k, v in lighting_counts.items()],
        }
    })

# === Heatmap Endpoint (on-demand) ===
@environment_bp.route('/heatmap', methods=['GET'])
def environment_heatmap():
    month = request.args.get('month', 'All')
    weather = request.args.get('weather', 'All')
    speed = request.args.get('speed', 'All')
    lighting = request.args.get('lighting', 'All')

    query = Crash.query
    if month != 'All':
        query = query.filter(Crash.crash_month == int(month))
    if weather != 'All':
        query = query.filter(Crash.weather_condition == weather)
    if speed != 'All':
        query = query.filter(Crash.posted_speed_limit == int(speed))
    if lighting != 'All':
        query = query.filter(Crash.lighting_condition == lighting)

    crashes = query.with_entities(Crash.latitude, Crash.longitude).all()

    crash_data = [(lat, lon) for lat, lon in crashes if lat and lon]

    if not crash_data:
        return jsonify({"map_path": None})

    if len(crash_data) > 2000:
        crash_data = crash_data[:2000]

    avg_lat = sum(lat for lat, _ in crash_data) / len(crash_data)
    avg_lon = sum(lon for _, lon in crash_data) / len(crash_data)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=11)
    HeatMap(crash_data, radius=12, blur=20, min_opacity=0.4).add_to(m)

    map_dir = os.path.join('app', 'static', 'maps')
    os.makedirs(map_dir, exist_ok=True)

    map_path = os.path.join(map_dir, 'environment_heatmap.html')
    m.save(map_path)

    return jsonify({"map_path": "/static/maps/environment_heatmap.html"})
