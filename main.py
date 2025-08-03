from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from config import Config
from main.models.models import db, Crash
from main.routes.offense import offense_bp
from main.routes.impact import impact_bp
from main.routes.location import location_bp
from main.routes.environment import environment_bp
import json

# Create Flask app with correct template and static folders
app = Flask(__name__, 
           template_folder='app/templates',
           static_folder='app/static')
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(offense_bp)
app.register_blueprint(impact_bp)
app.register_blueprint(location_bp)
app.register_blueprint(environment_bp)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', data=SAMPLE_DATA)

@app.route('/landing')
def landing():
    """Landing page"""
    return render_template('landing.html')


@app.route('/environment')
def environment():
    """Environmental Analysis Page"""
    return render_template('environment.html', data=SAMPLE_DATA)

@app.route('/api/chart-data')
def chart_data():
    """API endpoint for chart data"""
    return jsonify(SAMPLE_DATA['medals_by_country'])

if __name__ == '__main__':
    print("🚀 Starting Traffic Crash Dashboard...")
    print("📍 Dashboard will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)