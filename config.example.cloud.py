import os

_unix_socket = os.environ.get('INSTANCE_UNIX_SOCKET')

DB_CONFIG = {
    'user':     os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASS'),
    'database': os.environ.get('DB_NAME', 'hospital_db'),
    # On GCP Cloud Run, INSTANCE_UNIX_SOCKET is set automatically via Cloud SQL proxy.
    # Locally, falls back to DB_HOST (default: localhost).
    **({'unix_socket': _unix_socket} if _unix_socket else {'host': os.environ.get('DB_HOST', 'localhost')}),
}

SECRET_KEY = os.environ.get('SECRET_KEY')

USERS = {
    'admin':  {'password': 'admin123',  'role': 'admin', 'name': 'Hospital Administrator'},
    'doctor': {'password': 'doctor123', 'role': 'staff', 'name': 'Dr. Staff'},
    'nurse':  {'password': 'nurse123',  'role': 'staff', 'name': 'Nurse Staff'},
}
