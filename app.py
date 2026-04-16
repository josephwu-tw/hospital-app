from flask import Flask, render_template
from config import SECRET_KEY
from routes.patients import patients_bp
from routes.appointments import appointments_bp
from routes.doctors import doctors_bp
from routes.billing import billing_bp
from routes.analytics import analytics_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(patients_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(doctors_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(analytics_bp)


@app.route('/')
def index():
    from db import execute_query
    stats = {
        'patients':     execute_query("SELECT COUNT(*) AS n FROM Patient",        one=True)['n'],
        'doctors':      execute_query("SELECT COUNT(*) AS n FROM Doctor",         one=True)['n'],
        'appointments': execute_query("SELECT COUNT(*) AS n FROM Appointment",    one=True)['n'],
        'waiting':      execute_query("SELECT COUNT(*) AS n FROM Queue WHERE queueStatus='Waiting'", one=True)['n'],
        'unpaid':       execute_query("SELECT COUNT(*) AS n FROM Billing WHERE paymentStatus='Unpaid'", one=True)['n'],
    }
    return render_template('index.html', stats=stats)


if __name__ == '__main__':
    app.run(debug=True)
