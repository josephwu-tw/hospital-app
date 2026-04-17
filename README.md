# Intelligent Hospital Resource & Queue Management System

> CS5200 Database Management Systems · Spring 2026 · Group 10

A full-stack web application for managing hospital operations including patient registration, appointment scheduling, queue management, medical records, billing, and operational analytics — backed by a normalized MySQL relational database.

---

## Team

| Name | Role |
|---|---|
| Chen-Yen Wu | Full-stack development, database design |
| Jiani He | Database design, analytics queries |
| Yen-Wei Lin | Backend routes, SQL scripts |
| Zhenyu Wang | Schema design, data modeling |

---

## Features

- **User Authentication** — Session-based login with role support (Admin, Staff)
- **Patient Management** — Register, view, edit, and delete patient profiles
- **Doctor Management** — Manage doctors with department and specialization info
- **Appointment Scheduling** — Book, edit, cancel, and reschedule appointments
- **Queue Management** — Add patients to queue; calling a patient atomically completes the appointment and updates the queue via stored procedure; auto-refreshing live view with wait duration
- **Medical Records** — Create and manage treatment records linked to appointments
- **Billing** — Track payments, outstanding balances, and payment status
- **Departments & Rooms** — Manage hospital departments and room allocations
- **Analytics Dashboard** — 16 operational SQL queries organized across 5 tabs
- **Database Schema** — Interactive schema reference showing all 16 tables, relationships, and advanced DB objects
- **Live Table Search** — Client-side search and sortable columns on all list pages
- **Status Filters** — Filter appointments by Scheduled / Completed / Canceled / Rescheduled

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 · Flask |
| Database | MySQL 8 |
| Frontend | Jinja2 · Bootstrap 5.3 · Vanilla JavaScript |
| Icons | Bootstrap Icons 1.11 |

---

## Prerequisites

- Python 3.9+
- MySQL 8.0+
- pip

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd hospital-app
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database connection

`config.py` is excluded from version control. Copy the example file and fill in your MySQL password:

```bash
cp config.example.py config.py
```

Then edit `config.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',
    'database': 'hospital_db',
}

SECRET_KEY = 'any-random-string-you-want'  # e.g. 'mygroupproject2026'

USERS = {
    'admin':  {'password': 'admin123',  'role': 'admin', 'name': 'Hospital Administrator'},
    'doctor': {'password': 'doctor123', 'role': 'staff', 'name': 'Dr. Staff'},
    'nurse':  {'password': 'nurse123',  'role': 'staff', 'name': 'Nurse Staff'},
}
```

### 5. Create the database and load sample data

```bash
mysql -u root -p < sql/dbDDL.sql
mysql -u root -p < sql/dbDML.sql
```

To reset the database at any time:

```bash
mysql -u root -p < sql/dbDROP.sql
mysql -u root -p < sql/dbDDL.sql
mysql -u root -p < sql/dbDML.sql
```

### 6. Run the application

```bash
python app.py
```

Open **http://127.0.0.1:5001** in your browser.

> **macOS note:** Port 5000 is occupied by AirPlay Receiver on macOS Monterey and later, which causes a 403 error. The app runs on port 5001 to avoid this conflict. You can disable AirPlay Receiver under System Settings → General → AirDrop & Handoff if you prefer port 5000.

---

## Login Credentials

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Hospital Administrator |
| `doctor` | `doctor123` | Medical Staff |
| `nurse` | `nurse123` | Nurse Staff |

---

## Project Structure

```
hospital-app/
├── app.py                  # Flask app entry point
├── config.py               # DB config and user credentials
├── db.py                   # MySQL connection and query helpers
├── requirements.txt        # Python dependencies
├── routes/
│   ├── auth.py             # Login / logout
│   ├── patients.py         # Patient CRUD
│   ├── appointments.py     # Appointment CRUD
│   ├── doctors.py          # Doctor CRUD
│   ├── queue.py            # Queue management
│   ├── records.py          # Medical records CRUD
│   ├── billing.py          # Billing management
│   ├── departments.py      # Department CRUD
│   ├── rooms.py            # Room CRUD
│   └── analytics.py        # 16 analytics queries
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── schema.html             # Interactive DB schema reference
│   ├── auth/
│   ├── patients/
│   ├── appointments/
│   ├── doctors/
│   ├── queue/
│   ├── records/
│   ├── billing/
│   ├── departments/
│   ├── rooms/
│   └── analytics/
├── static/
│   └── js/app.js           # Live search, sort, delete modal, queue refresh
└── sql/
    ├── dbDDL.sql           # Schema: tables, indexes, views, triggers, procedures
    ├── dbDML.sql           # Sample data
    ├── dbDROP.sql          # Drop all objects
    └── dbSQL.sql           # Advanced queries
```

---

## Database Schema

The database contains **16 tables** implementing a fully normalized relational schema:

`Person` · `Patient` · `Staff` · `Doctor` · `Nurse` · `Department` · `Room` · `Appointment` · `Queue` · `MedicalRecord` · `MedicalDevice` · `Record_Device` · `Billing` · `Insurance` · `Patient_Insurance` · `Nurse_Department`

Key design features:
- **Generalization hierarchy**: `Person → Patient / Staff → Doctor / Nurse`
- **Weak entity**: `Queue` identified by `(appointmentID, queuePos)`
- **Trigger**: auto-creates a `Billing` record on appointment insert
- **View**: `v_waiting_patients` for real-time queue visibility
- **Stored procedure**: `sp_complete_appointment` marks appointment complete and updates queue

---

## Analytics Queries

The analytics dashboard implements all 16 queries from the project specification, organized across tabs:

| Tab | Queries |
|---|---|
| Queue & Wait | Q1 Waiting patients · Q2 Avg wait per dept · Q7 Peak hours · Q8 Late patients · Q15 Before/after policy comparison |
| Appointments | Q3 Busiest doctors · Q5 Canceled/rescheduled · Q9 Consultation duration · Q10 Dept volume · Q16 Cancellation rates |
| Resources | Q4 Device utilization >90% · Q13 Idle equipment |
| Billing | Q11 Overdue unpaid bills · Q12 Frequent visitors |
| Reports | Q6 Full treatment history · Q14 Daily appointment report |
