from flask import Flask, render_template, session, redirect, url_for, request
from config import SECRET_KEY
from routes.auth import auth_bp
from routes.patients import patients_bp
from routes.appointments import appointments_bp
from routes.doctors import doctors_bp
from routes.billing import billing_bp
from routes.analytics import analytics_bp
from routes.queue import queue_bp
from routes.records import records_bp
from routes.departments import departments_bp
from routes.rooms import rooms_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(doctors_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(queue_bp)
app.register_blueprint(records_bp)
app.register_blueprint(departments_bp)
app.register_blueprint(rooms_bp)

PUBLIC_ENDPOINTS = {'auth.login', 'auth.logout', 'static'}


@app.before_request
def require_login():
    if request.endpoint in PUBLIC_ENDPOINTS:
        return
    if 'user' not in session:
        return redirect(url_for('auth.login'))


@app.route('/')
def index():
    from db import execute_query
    stats = {
        'patients':     execute_query("SELECT COUNT(*) AS n FROM Patient",        one=True)['n'],
        'doctors':      execute_query("SELECT COUNT(*) AS n FROM Doctor",         one=True)['n'],
        'appointments': execute_query("SELECT COUNT(*) AS n FROM Appointment",    one=True)['n'],
        'waiting':      execute_query("SELECT COUNT(*) AS n FROM Queue WHERE queueStatus='Waiting'", one=True)['n'],
        'unpaid':       execute_query("SELECT COUNT(*) AS n FROM Billing WHERE paymentStatus='Unpaid'", one=True)['n'],
        'records':      execute_query("SELECT COUNT(*) AS n FROM MedicalRecord",  one=True)['n'],
        'departments':  execute_query("SELECT COUNT(*) AS n FROM Department",     one=True)['n'],
        'rooms':        execute_query("SELECT COUNT(*) AS n FROM Room",           one=True)['n'],
    }
    recent_appts = execute_query("""
        SELECT a.appointmentID, a.scheduledDateTime, a.status, a.appointmentType,
               CONCAT(p.firstName, ' ', p.lastName) AS patientName,
               CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName
        FROM Appointment a
        JOIN Person p   ON a.patientID = p.personID
        JOIN Person doc ON a.doctorID  = doc.personID
        ORDER BY a.scheduledDateTime DESC
        LIMIT 5
    """)
    return render_template('index.html', stats=stats, recent_appts=recent_appts)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
