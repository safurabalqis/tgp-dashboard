from flask import Flask, render_template, request, jsonify
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from app.models.models import db, Crash
import json

# Create Flask app with correct template and static folders
app = Flask(__name__, 
           template_folder='app/templates',
           static_folder='app/static')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)

# Sample Olympics data
SAMPLE_DATA = {
    'countries': 92,
    'disciplines': 45,
    'events': 288,
    'medallists': 2053,
    'athletes': 11113,
    'medals_by_country': [
        {'country': 'USA', 'gold': 40, 'silver': 44, 'bronze': 42, 'total': 126},
        {'country': 'China', 'gold': 38, 'silver': 32, 'bronze': 21, 'total': 91},
        {'country': 'Japan', 'gold': 20, 'silver': 12, 'bronze': 33, 'total': 65},
        {'country': 'Australia', 'gold': 18, 'silver': 19, 'bronze': 27, 'total': 64},
        {'country': 'France', 'gold': 16, 'silver': 26, 'bronze': 11, 'total': 53},
        {'country': 'Netherlands', 'gold': 15, 'silver': 7, 'bronze': 23, 'total': 45},
        {'country': 'Great Britain', 'gold': 14, 'silver': 22, 'bronze': 4, 'total': 40},
        {'country': 'South Korea', 'gold': 13, 'silver': 9, 'bronze': 12, 'total': 34},
        {'country': 'Italy', 'gold': 12, 'silver': 13, 'bronze': 8, 'total': 33},
        {'country': 'Germany', 'gold': 12, 'silver': 13, 'bronze': 7, 'total': 32}
    ]
}

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', data=SAMPLE_DATA)

@app.route('/landing')
def landing():
    """Landing page"""
    return render_template('landing.html')

@app.route('/athletes')
def athletes():
    """Athletes analysis page"""
    return render_template('athletes.html', data=SAMPLE_DATA)

@app.route('/impact')
def impact():
    # Query the crash_type and count how many times each type appears
    crash_data = (
        db.session.query(Crash.crash_type, db.func.count(Crash.crash_record_id))
        .group_by(Crash.crash_type)
        .order_by(db.func.count(Crash.crash_record_id).desc())
        .all()
    )

    # Prepare data for Chart.js
    labels = [row[0] if row[0] else 'Unknown' for row in crash_data]
    values = [row[1] for row in crash_data]

    return render_template('impact.html', labels=labels, values=values)


@app.route('/sports')
def sports():
    """Sports analysis page"""
    return render_template('sports.html', data=SAMPLE_DATA)

@app.route('/api/chart-data')
def chart_data():
    """API endpoint for chart data"""
    return jsonify(SAMPLE_DATA['medals_by_country'])

if __name__ == '__main__':
    print("🚀 Starting Olympics Dashboard...")
    print("📍 Dashboard will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)