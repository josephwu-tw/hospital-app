DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', # Replace with your actual MySQL username
    'password': 'YOUR_MYSQL_PASSWORD', # Replace with your actual MySQL password
    'database': 'hospital_db', # Ensure this matches the name of your MySQL database
}

SECRET_KEY = 'YOUR_SECRET_KEY' # Replace with a strong, random secret key for session management and security

USERS = {
    'admin':  {'password': 'admin123',  'role': 'admin', 'name': 'Hospital Administrator'},
    'doctor': {'password': 'doctor123', 'role': 'staff', 'name': 'Dr. Staff'},
    'nurse':  {'password': 'nurse123',  'role': 'staff', 'name': 'Nurse Staff'},
}
