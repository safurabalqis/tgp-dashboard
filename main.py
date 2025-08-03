from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from config import Config
from app.models.models import db, Crash
from app.routes.offense import offense_bp
from app.routes.impact import impact_bp
from app.routes.location import location_bp
from app.routes.environment import environment_bp
from app.routes.chatbot import chatbot_bp
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
app.register_blueprint(chatbot_bp)



@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')




if __name__ == '__main__':
    print("🚀 Starting CrashStat...")
    print("📍 Dashboard will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)