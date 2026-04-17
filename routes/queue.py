from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

queue_bp = Blueprint('queue', __name__)

_LIST_SQL = """
    SELECT q.appointmentID, q.queuePos, q.arrivalTime, q.calledTime, q.queueStatus,
           CONCAT(p.firstName, ' ', p.lastName) AS patientName,
           CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
           d.deptName, a.scheduledDateTime, a.appointmentType,
           fn_wait_duration(q.appointmentID, q.queuePos) AS waitMinutes
    FROM Queue q
    JOIN Appointment a  ON q.appointmentID = a.appointmentID
    JOIN Person p       ON a.patientID     = p.personID
    JOIN Person doc     ON a.doctorID      = doc.personID
    LEFT JOIN Room r    ON a.roomID        = r.roomID
    LEFT JOIN Department d ON r.deptID     = d.deptID
    ORDER BY
        FIELD(q.queueStatus, 'Waiting', 'Served') ASC,
        q.arrivalTime ASC
"""


@queue_bp.route('/queue')
def list_queue():
    entries = execute_query(_LIST_SQL)
    waiting = sum(1 for e in entries if e['queueStatus'] == 'Waiting')
    return render_template('queue/list.html', entries=entries, waiting=waiting)


@queue_bp.route('/queue/add', methods=['GET', 'POST'])
def add_to_queue():
    appointments = execute_query("""
        SELECT a.appointmentID,
               CONCAT(p.firstName, ' ', p.lastName) AS patientName,
               CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
               a.scheduledDateTime, a.appointmentType
        FROM Appointment a
        JOIN Person p   ON a.patientID = p.personID
        JOIN Person doc ON a.doctorID  = doc.personID
        WHERE a.status = 'Scheduled'
          AND a.appointmentID NOT IN (
              SELECT appointmentID FROM Queue WHERE queueStatus = 'Waiting'
          )
        ORDER BY a.scheduledDateTime
    """)
    if request.method == 'POST':
        try:
            aid = int(request.form['appointmentID'])
            next_pos = execute_query(
                "SELECT COALESCE(MAX(queuePos), 0) + 1 AS nxt FROM Queue WHERE appointmentID = %s",
                (aid,), one=True
            )['nxt']
            execute_update(
                """INSERT INTO Queue (appointmentID, queuePos, arrivalTime, queueStatus)
                   VALUES (%s, %s, NOW(), 'Waiting')""",
                (aid, next_pos)
            )
            flash('Patient added to queue.', 'success')
            return redirect(url_for('queue.list_queue'))
        except Exception as e:
            flash(f'Error adding to queue: {e}', 'danger')
    return render_template('queue/form.html', appointments=appointments)


@queue_bp.route('/queue/<int:aid>/<int:pos>/call', methods=['POST'])
def call_patient(aid, pos):
    try:
        execute_update("CALL sp_complete_appointment(%s, NOW())", (aid,))
        flash('Patient called — appointment marked Completed.', 'success')
    except Exception as e:
        flash(f'Error calling patient: {e}', 'danger')
    return redirect(url_for('queue.list_queue'))


@queue_bp.route('/queue/<int:aid>/<int:pos>/delete', methods=['POST'])
def delete_queue(aid, pos):
    try:
        execute_update(
            "DELETE FROM Queue WHERE appointmentID=%s AND queuePos=%s",
            (aid, pos)
        )
        flash('Queue entry removed.', 'success')
    except Exception as e:
        flash(f'Error removing from queue: {e}', 'danger')
    return redirect(url_for('queue.list_queue'))
