from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from config import Config
from app.models.models import db, Crash
from app.routes.offense import offense_bp
from app.routes.impact import impact_bp
from app.routes.location import location_bp
from app.routes.environment import environment_bp
from app.routes.chatbot import chatbot_bp
from app.routes.auth import auth_bp
import json
from datetime import timedelta

# ─────────────────────────────
# Initialize Flask App
# ─────────────────────────────
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')
app.config.from_object(Config)

# ─────────────────────────────
# Register Blueprints
# ─────────────────────────────
db.init_app(app)
app.register_blueprint(offense_bp)
app.register_blueprint(impact_bp)
app.register_blueprint(location_bp)
app.register_blueprint(environment_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(auth_bp)

# ─────────────────────────────
# Restrict access to all routes except dashboard and auth
# ─────────────────────────────
@app.before_request
def require_login():
    allowed_routes = ['dashboard', 'auth.login', 'auth.register', 'static']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('dashboard'))

# ─────────────────────────────
# Default Welcome Page
# ─────────────────────────────
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

# ─────────────────────────────
# Start App
# ─────────────────────────────
if __name__ == '__main__':
    print("🚀 Starting CrashStat...")
    print("📍 Dashboard will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
