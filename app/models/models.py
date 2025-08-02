from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Crash(db.Model):
    __tablename__ = 'traffic_crashes'

    crash_record_id = db.Column(db.String, primary_key=True, name="CRASH_RECORD_ID")
    crash_date = db.Column(db.DateTime, name="CRASH_DATE")
    posted_speed_limit = db.Column(db.Integer, name="POSTED_SPEED_LIMIT")
    traffic_control_device = db.Column(db.String, name="TRAFFIC_CONTROL_DEVICE")
    weather_condition = db.Column(db.String, name="WEATHER_CONDITION")
    light_condition = db.Column(db.String, name="LIGHT_CONDITION")
    injuries_total = db.Column(db.Integer, name="INJURIES_TOTAL")
    injuries_fatal = db.Column(db.Integer, name="INJURIES_FATAL")
    injuries_incapacitating = db.Column(db.Integer, name="INJURIES_INCAPACITATING")
    injuries_non_incapacitating = db.Column(db.Integer, name="INJURIES_NON_INCAPACITATING")
    injuries_no_indication = db.Column(db.Integer, name="INJURIES_NO_INDICATION")
    crash_hour = db.Column(db.Integer, name="CRASH_HOUR")
    crash_day_of_week = db.Column(db.Integer, name="CRASH_DAY_OF_WEEK")
    crash_month = db.Column(db.Integer, name="CRASH_MONTH")
    latitude = db.Column(db.Float, name="LATITUDE")
    longitude = db.Column(db.Float, name="LONGITUDE")
    location = db.Column(db.String, name="LOCATION")
    crash_type = db.Column(db.String(50), name="CRASH_TYPE")
