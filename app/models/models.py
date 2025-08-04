from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Crash(db.Model):
    __tablename__ = 'traffic_crashes'

    crash_record_id                = db.Column(db.String,     primary_key=True, name="CRASH_RECORD_ID")
    crash_date_est_i               = db.Column(db.String,     name="CRASH_DATE_EST_I")
    crash_date                     = db.Column(db.String,     name="CRASH_DATE")
    posted_speed_limit             = db.Column(db.BigInteger,  name="POSTED_SPEED_LIMIT")
    traffic_control_device         = db.Column(db.String,     name="TRAFFIC_CONTROL_DEVICE")
    device_condition               = db.Column(db.String,     name="DEVICE_CONDITION")
    weather_condition              = db.Column(db.String,     name="WEATHER_CONDITION")
    lighting_condition             = db.Column(db.String,     name="LIGHTING_CONDITION")
    first_crash_type               = db.Column(db.String,     name="FIRST_CRASH_TYPE")
    trafficway_type                = db.Column(db.String,     name="TRAFFICWAY_TYPE")
    lane_cnt                       = db.Column(db.Float,      name="LANE_CNT")
    alignment                      = db.Column(db.String,     name="ALIGNMENT")
    roadway_surface_cond           = db.Column(db.String,     name="ROADWAY_SURFACE_COND")
    road_defect                    = db.Column(db.String,     name="ROAD_DEFECT")
    report_type                    = db.Column(db.String,     name="REPORT_TYPE")
    crash_type                     = db.Column(db.String(50), name="CRASH_TYPE")

    intersection_related_i         = db.Column(db.String,     name="INTERSECTION_RELATED_I")
    not_right_of_way_i             = db.Column(db.String,     name="NOT_RIGHT_OF_WAY_I")
    hit_and_run_i                  = db.Column(db.String,     name="HIT_AND_RUN_I")
    damage                         = db.Column(db.String,     name="DAMAGE")
    date_police_notified           = db.Column(db.String,     name="DATE_POLICE_NOTIFIED")

    prim_contributory_cause        = db.Column(db.String,     name="PRIM_CONTRIBUTORY_CAUSE")
    sec_contributory_cause         = db.Column(db.String,     name="SEC_CONTRIBUTORY_CAUSE")

    street_no                      = db.Column(db.BigInteger,  name="STREET_NO")
    street_direction               = db.Column(db.String,     name="STREET_DIRECTION")
    street_name                    = db.Column(db.String,     name="STREET_NAME")
    beat_of_occurrence             = db.Column(db.BigInteger,  name="BEAT_OF_OCCURRENCE")

    photos_taken_i                 = db.Column(db.String,     name="PHOTOS_TAKEN_I")
    statements_taken_i             = db.Column(db.String,     name="STATEMENTS_TAKEN_I")
    dooring_i                      = db.Column(db.String,     name="DOORING_I")
    work_zone_i                    = db.Column(db.String,     name="WORK_ZONE_I")
    work_zone_type                 = db.Column(db.String,     name="WORK_ZONE_TYPE")
    workers_present_i              = db.Column(db.String,     name="WORKERS_PRESENT_I")

    num_units                      = db.Column(db.BigInteger,  name="NUM_UNITS")
    most_severe_injury             = db.Column(db.String,     name="MOST_SEVERE_INJURY")

    injuries_total                 = db.Column(db.Float,      name="INJURIES_TOTAL")
    injuries_fatal                 = db.Column(db.Float,      name="INJURIES_FATAL")
    injuries_incapacitating        = db.Column(db.Float,      name="INJURIES_INCAPACITATING")
    injuries_non_incapacitating    = db.Column(db.Float,      name="INJURIES_NON_INCAPACITATING")
    injuries_reported_not_evident  = db.Column(db.Float,      name="INJURIES_REPORTED_NOT_EVIDENT")
    injuries_no_indication         = db.Column(db.Float,      name="INJURIES_NO_INDICATION")
    injuries_unknown               = db.Column(db.Float,      name="INJURIES_UNKNOWN")

    crash_hour                     = db.Column(db.BigInteger,  name="CRASH_HOUR")
    crash_day_of_week              = db.Column(db.BigInteger,  name="CRASH_DAY_OF_WEEK")
    crash_month                    = db.Column(db.BigInteger,  name="CRASH_MONTH")
    latitude                       = db.Column(db.Float,      name="LATITUDE")
    longitude                      = db.Column(db.Float,      name="LONGITUDE")
    location                       = db.Column(db.String,     name="LOCATION")

class User(db.Model):
    __tablename__ = 'users'
    
    user_id         = db.Column('id', db.Integer, primary_key=True)
    user_name       = db.Column('username', db.String, nullable=False)
    user_email      = db.Column('email', db.String, unique=True, nullable=False)
    user_password   = db.Column('password_hash', db.String, nullable=False)
    user_active     = db.Column('is_active', db.Boolean, default=True)
    
