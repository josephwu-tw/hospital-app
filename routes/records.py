from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

records_bp = Blueprint('records', __name__)

_LIST_SQL = """
    SELECT mr.recordID, mr.recordDate, mr.diagnosis,
           CONCAT(p.firstName, ' ', p.lastName) AS patientName,
           CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
           a.appointmentID, a.scheduledDateTime, a.appointmentType
    FROM MedicalRecord mr
    JOIN Appointment a  ON mr.appointmentID = a.appointmentID
    JOIN Person p       ON a.patientID      = p.personID
    JOIN Person doc     ON a.doctorID       = doc.personID
    ORDER BY mr.recordDate DESC
"""

_DETAIL_SQL = """
    SELECT mr.*,
           CONCAT(p.firstName, ' ', p.lastName)   AS patientName,
           CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
           a.scheduledDateTime, a.appointmentType
    FROM MedicalRecord mr
    JOIN Appointment a  ON mr.appointmentID = a.appointmentID
    JOIN Person p       ON a.patientID      = p.personID
    JOIN Person doc     ON a.doctorID       = doc.personID
    WHERE mr.recordID = %s
"""

_DEVICES_SQL = """
    SELECT rd.usageDate, rd.duration, rd.usagePurpose,
           md.deviceName, md.deviceType
    FROM Record_Device rd
    JOIN MedicalDevice md ON rd.deviceID = md.deviceID
    WHERE rd.recordID = %s
    ORDER BY rd.usageDate
"""


@records_bp.route('/records')
def list_records():
    records = execute_query(_LIST_SQL)
    return render_template('records/list.html', records=records)


@records_bp.route('/records/<int:rid>')
def view_record(rid):
    record = execute_query(_DETAIL_SQL, (rid,), one=True)
    if not record:
        flash('Medical record not found.', 'danger')
        return redirect(url_for('records.list_records'))
    devices = execute_query(_DEVICES_SQL, (rid,))
    return render_template('records/detail.html', record=record, devices=devices)


@records_bp.route('/records/new', methods=['GET', 'POST'])
def new_record():
    appointments = execute_query("""
        SELECT a.appointmentID,
               CONCAT(p.firstName, ' ', p.lastName) AS patientName,
               CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
               a.scheduledDateTime
        FROM Appointment a
        JOIN Person p   ON a.patientID = p.personID
        JOIN Person doc ON a.doctorID  = doc.personID
        WHERE a.appointmentID NOT IN (SELECT appointmentID FROM MedicalRecord)
        ORDER BY a.scheduledDateTime DESC
    """)
    preselect = request.args.get('appointment')
    if request.method == 'POST':
        try:
            execute_update(
                """INSERT INTO MedicalRecord
                       (appointmentID, recordDate, diagnosis, treatmentPlan,
                        prescriptions, labResults)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    request.form['appointmentID'],
                    request.form['recordDate'],
                    request.form['diagnosis'].strip() or None,
                    request.form['treatmentPlan'].strip() or None,
                    request.form['prescriptions'].strip() or None,
                    request.form['labResults'].strip() or None,
                )
            )
            flash('Medical record created.', 'success')
            return redirect(url_for('records.list_records'))
        except Exception as e:
            flash(f'Error creating record: {e}', 'danger')
    return render_template('records/form.html',
                           record=None, appointments=appointments,
                           preselect=preselect, action='Create')


@records_bp.route('/records/<int:rid>/edit', methods=['GET', 'POST'])
def edit_record(rid):
    record = execute_query(_DETAIL_SQL, (rid,), one=True)
    if not record:
        flash('Medical record not found.', 'danger')
        return redirect(url_for('records.list_records'))
    if request.method == 'POST':
        try:
            execute_update(
                """UPDATE MedicalRecord
                   SET recordDate=%s, diagnosis=%s, treatmentPlan=%s,
                       prescriptions=%s, labResults=%s
                   WHERE recordID=%s""",
                (
                    request.form['recordDate'],
                    request.form['diagnosis'].strip() or None,
                    request.form['treatmentPlan'].strip() or None,
                    request.form['prescriptions'].strip() or None,
                    request.form['labResults'].strip() or None,
                    rid,
                )
            )
            flash('Medical record updated.', 'success')
            return redirect(url_for('records.view_record', rid=rid))
        except Exception as e:
            flash(f'Error updating record: {e}', 'danger')
    return render_template('records/form.html',
                           record=record, appointments=None,
                           preselect=None, action='Edit')


@records_bp.route('/records/<int:rid>/delete', methods=['POST'])
def delete_record(rid):
    try:
        execute_update("DELETE FROM MedicalRecord WHERE recordID = %s", (rid,))
        flash('Medical record deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting record: {e}', 'danger')
    return redirect(url_for('records.list_records'))
