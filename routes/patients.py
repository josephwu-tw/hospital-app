from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

patients_bp = Blueprint('patients', __name__)

_LIST_SQL = """
    SELECT p.personID, p.firstName, p.lastName, p.phone, p.email,
           p.dateOfBirth, pat.bloodType, pat.allergies, pat.emergencyContact
    FROM Person p
    JOIN Patient pat ON p.personID = pat.personID
    ORDER BY p.lastName, p.firstName
"""

_DETAIL_SQL = """
    SELECT p.personID, p.firstName, p.lastName, p.dateOfBirth,
           p.phone, p.email, p.address,
           pat.bloodType, pat.allergies, pat.emergencyContact
    FROM Person p
    JOIN Patient pat ON p.personID = pat.personID
    WHERE p.personID = %s
"""

_APPT_HISTORY_SQL = """
    SELECT a.appointmentID, a.scheduledDateTime, a.status, a.appointmentType,
           CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
           dept.deptName, b.totalAmount, b.amountPaid, b.paymentStatus
    FROM Appointment a
    JOIN Person doc ON a.doctorID = doc.personID
    JOIN Doctor dr  ON a.doctorID = dr.personID
    JOIN Department dept ON dr.deptID = dept.deptID
    LEFT JOIN Billing b ON a.appointmentID = b.appointmentID
    WHERE a.patientID = %s
    ORDER BY a.scheduledDateTime DESC
"""


@patients_bp.route('/patients')
def list_patients():
    patients = execute_query(_LIST_SQL)
    return render_template('patients/list.html', patients=patients)


@patients_bp.route('/patients/<int:pid>')
def view_patient(pid):
    patient = execute_query(_DETAIL_SQL, (pid,), one=True)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.list_patients'))
    appointments = execute_query(_APPT_HISTORY_SQL, (pid,))
    return render_template('patients/detail.html', patient=patient, appointments=appointments)


@patients_bp.route('/patients/new', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        try:
            pid = execute_update(
                """INSERT INTO Person (firstName, lastName, dateOfBirth, phone, email, address)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    request.form['firstName'].strip(),
                    request.form['lastName'].strip(),
                    request.form['dateOfBirth'],
                    request.form['phone'].strip() or None,
                    request.form['email'].strip() or None,
                    request.form['address'].strip() or None,
                )
            )
            execute_update(
                """INSERT INTO Patient (personID, bloodType, allergies, emergencyContact)
                   VALUES (%s, %s, %s, %s)""",
                (
                    pid,
                    request.form.get('bloodType') or None,
                    request.form.get('allergies').strip() or None,
                    request.form.get('emergencyContact').strip() or None,
                )
            )
            flash('Patient created successfully.', 'success')
            return redirect(url_for('patients.view_patient', pid=pid))
        except Exception as e:
            flash(f'Error creating patient: {e}', 'danger')
    return render_template('patients/form.html', patient=None, action='Create')


@patients_bp.route('/patients/<int:pid>/edit', methods=['GET', 'POST'])
def edit_patient(pid):
    patient = execute_query(_DETAIL_SQL, (pid,), one=True)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.list_patients'))
    if request.method == 'POST':
        try:
            execute_update(
                """UPDATE Person SET firstName=%s, lastName=%s, dateOfBirth=%s,
                       phone=%s, email=%s, address=%s
                   WHERE personID=%s""",
                (
                    request.form['firstName'].strip(),
                    request.form['lastName'].strip(),
                    request.form['dateOfBirth'],
                    request.form['phone'].strip() or None,
                    request.form['email'].strip() or None,
                    request.form['address'].strip() or None,
                    pid,
                )
            )
            execute_update(
                """UPDATE Patient SET bloodType=%s, allergies=%s, emergencyContact=%s
                   WHERE personID=%s""",
                (
                    request.form.get('bloodType') or None,
                    request.form.get('allergies').strip() or None,
                    request.form.get('emergencyContact').strip() or None,
                    pid,
                )
            )
            flash('Patient updated successfully.', 'success')
            return redirect(url_for('patients.view_patient', pid=pid))
        except Exception as e:
            flash(f'Error updating patient: {e}', 'danger')
    return render_template('patients/form.html', patient=patient, action='Edit')


@patients_bp.route('/patients/<int:pid>/delete', methods=['POST'])
def delete_patient(pid):
    try:
        execute_update("DELETE FROM Person WHERE personID = %s", (pid,))
        flash('Patient deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting patient: {e}', 'danger')
    return redirect(url_for('patients.list_patients'))
