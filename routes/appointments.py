from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

appointments_bp = Blueprint('appointments', __name__)

_LIST_SQL = """
    SELECT a.appointmentID, a.scheduledDateTime, a.actualStartTime,
           a.status, a.appointmentType, a.rescheduleCount,
           CONCAT(pat.firstName, ' ', pat.lastName) AS patientName,
           CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
           r.roomNumber, dept.deptName
    FROM Appointment a
    JOIN Person pat   ON a.patientID = pat.personID
    JOIN Person doc   ON a.doctorID  = doc.personID
    LEFT JOIN Room r  ON a.roomID    = r.roomID
    LEFT JOIN Department dept ON r.deptID = dept.deptID
    ORDER BY a.scheduledDateTime DESC
"""

_DETAIL_SQL = """
    SELECT a.*,
           CONCAT(pat.firstName, ' ', pat.lastName) AS patientName,
           CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
           r.roomNumber
    FROM Appointment a
    JOIN Person pat   ON a.patientID = pat.personID
    JOIN Person doc   ON a.doctorID  = doc.personID
    LEFT JOIN Room r  ON a.roomID    = r.roomID
    WHERE a.appointmentID = %s
"""


def _get_dropdowns():
    patients = execute_query(
        "SELECT p.personID, CONCAT(p.firstName, ' ', p.lastName) AS name "
        "FROM Person p JOIN Patient pat ON p.personID = pat.personID ORDER BY p.lastName"
    )
    doctors = execute_query(
        "SELECT d.personID, CONCAT(p.firstName, ' ', p.lastName) AS name, dept.deptName "
        "FROM Doctor d JOIN Person p ON d.personID = p.personID "
        "JOIN Department dept ON d.deptID = dept.deptID ORDER BY p.lastName"
    )
    rooms = execute_query(
        "SELECT r.roomID, r.roomNumber, dept.deptName "
        "FROM Room r JOIN Department dept ON r.deptID = dept.deptID ORDER BY r.roomNumber"
    )
    return patients, doctors, rooms


@appointments_bp.route('/appointments')
def list_appointments():
    appointments = execute_query(_LIST_SQL)
    return render_template('appointments/list.html', appointments=appointments)


@appointments_bp.route('/appointments/new', methods=['GET', 'POST'])
def new_appointment():
    patients, doctors, rooms = _get_dropdowns()
    if request.method == 'POST':
        try:
            execute_update(
                """INSERT INTO Appointment
                       (scheduledDateTime, appointmentType, status, rescheduleCount,
                        patientID, doctorID, roomID)
                   VALUES (%s, %s, 'Scheduled', 0, %s, %s, %s)""",
                (
                    request.form['scheduledDateTime'],
                    request.form['appointmentType'],
                    request.form['patientID'],
                    request.form['doctorID'],
                    request.form['roomID'] or None,
                )
            )
            flash('Appointment scheduled successfully.', 'success')
            return redirect(url_for('appointments.list_appointments'))
        except Exception as e:
            flash(f'Error scheduling appointment: {e}', 'danger')
    return render_template('appointments/form.html',
                           appointment=None, patients=patients,
                           doctors=doctors, rooms=rooms, action='Schedule')


@appointments_bp.route('/appointments/<int:aid>/edit', methods=['GET', 'POST'])
def edit_appointment(aid):
    appointment = execute_query(_DETAIL_SQL, (aid,), one=True)
    if not appointment:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    patients, doctors, rooms = _get_dropdowns()
    if request.method == 'POST':
        try:
            execute_update(
                """UPDATE Appointment
                   SET scheduledDateTime=%s, appointmentType=%s,
                       status=%s, rescheduleCount=%s
                   WHERE appointmentID=%s""",
                (
                    request.form['scheduledDateTime'],
                    request.form['appointmentType'],
                    request.form['status'],
                    request.form['rescheduleCount'],
                    aid,
                )
            )
            flash('Appointment updated.', 'success')
            return redirect(url_for('appointments.list_appointments'))
        except Exception as e:
            flash(f'Error updating appointment: {e}', 'danger')
    return render_template('appointments/form.html',
                           appointment=appointment, patients=patients,
                           doctors=doctors, rooms=rooms, action='Edit')


@appointments_bp.route('/appointments/<int:aid>/delete', methods=['POST'])
def delete_appointment(aid):
    try:
        execute_update("DELETE FROM Appointment WHERE appointmentID = %s", (aid,))
        flash('Appointment deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting appointment: {e}', 'danger')
    return redirect(url_for('appointments.list_appointments'))
