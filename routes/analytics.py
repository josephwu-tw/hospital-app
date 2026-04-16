from flask import Blueprint, render_template
from db import execute_query

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics')
def dashboard():
    # Query 1 — patients currently waiting, with dept info
    q1 = execute_query("""
        SELECT p.personID, p.firstName, p.lastName,
               d.deptName, q.queuePos, q.arrivalTime, q.queueStatus
        FROM Queue q
        JOIN Appointment a ON q.appointmentID = a.appointmentID
        JOIN Room        r ON a.roomID        = r.roomID
        JOIN Department  d ON r.deptID        = d.deptID
        JOIN Person      p ON a.patientID     = p.personID
        WHERE q.queueStatus = 'Waiting'
        ORDER BY q.arrivalTime
    """)

    # Query 2 — avg wait per department (> 10 min)
    q2 = execute_query("""
        SELECT d.deptName,
               ROUND(AVG(TIMESTAMPDIFF(MINUTE, q.arrivalTime, q.calledTime)), 2) AS avgWaitMinutes
        FROM Queue q
        JOIN Appointment a ON q.appointmentID = a.appointmentID
        JOIN Room        r ON a.roomID        = r.roomID
        JOIN Department  d ON r.deptID        = d.deptID
        WHERE q.calledTime IS NOT NULL
        GROUP BY d.deptName
        HAVING avgWaitMinutes > 10
        ORDER BY avgWaitMinutes DESC
    """)

    # Query 3 — doctors with 2+ appointments + avg billing
    q3 = execute_query("""
        SELECT doc.personID AS doctorID, p.firstName, p.lastName,
               COUNT(a.appointmentID)       AS totalAppointments,
               ROUND(AVG(b.totalAmount), 2) AS avgBillingAmount
        FROM Doctor doc
        JOIN Person      p  ON doc.personID    = p.personID
        JOIN Appointment a  ON doc.personID    = a.doctorID
        JOIN Billing     b  ON a.appointmentID = b.appointmentID
        GROUP BY doc.personID, p.firstName, p.lastName
        HAVING totalAppointments >= 2
        ORDER BY totalAppointments DESC
    """)

    # Query 4 — patients who waited 30+ minutes beyond scheduled time
    q4 = execute_query("""
        WITH late_waits AS (
            SELECT a.patientID, a.appointmentID, a.scheduledDateTime,
                   TIMESTAMPDIFF(MINUTE, q.arrivalTime, q.calledTime) AS waitMinutes
            FROM Queue q
            JOIN Appointment a ON q.appointmentID = a.appointmentID
            WHERE q.calledTime IS NOT NULL
        )
        SELECT lw.patientID, p.firstName, p.lastName,
               lw.appointmentID, lw.scheduledDateTime, lw.waitMinutes
        FROM late_waits lw
        JOIN Person p ON lw.patientID = p.personID
        WHERE lw.waitMinutes >= 30
        ORDER BY lw.waitMinutes DESC
    """)

    # Query 5 — unpaid billing records older than 30 days
    q5 = execute_query("""
        SELECT b.billingID,
               CONCAT(pat_p.firstName, ' ', pat_p.lastName) AS patientName,
               CONCAT(doc_p.firstName, ' ', doc_p.lastName) AS doctorName,
               b.totalAmount, b.billingDate,
               DATEDIFF(CURDATE(), b.billingDate) AS daysOverdue
        FROM Billing b
        JOIN Appointment a  ON b.appointmentID = a.appointmentID
        JOIN Person pat_p   ON a.patientID     = pat_p.personID
        JOIN Person doc_p   ON a.doctorID      = doc_p.personID
        WHERE b.paymentStatus = 'Unpaid'
          AND b.billingDate < DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        ORDER BY daysOverdue DESC
    """)

    # Query 6 — appointments canceled/rescheduled more than once
    q6 = execute_query("""
        SELECT a.appointmentID,
               CONCAT(pat.firstName, ' ', pat.lastName) AS patientName,
               CONCAT(doc.firstName, ' ', doc.lastName) AS doctorName,
               a.status, a.rescheduleCount, a.scheduledDateTime
        FROM Appointment a
        JOIN Person pat ON a.patientID = pat.personID
        JOIN Person doc ON a.doctorID  = doc.personID
        WHERE (a.status = 'Canceled' OR a.status = 'Rescheduled')
          AND a.rescheduleCount > 1
        ORDER BY a.rescheduleCount DESC
    """)

    # Query 7 — full treatment history for all patients (grouped by patient)
    q7 = execute_query("""
        SELECT a.appointmentID, a.scheduledDateTime,
               CONCAT(p.firstName, ' ', p.lastName) AS patientName,
               mr.diagnosis, mr.treatmentPlan, mr.prescriptions,
               md.deviceName, rd.usagePurpose
        FROM Appointment   a
        JOIN Person        p  ON a.patientID     = p.personID
        JOIN MedicalRecord mr ON a.appointmentID = mr.appointmentID
        LEFT JOIN Record_Device rd ON mr.recordID  = rd.recordID
        LEFT JOIN MedicalDevice md ON rd.deviceID  = md.deviceID
        ORDER BY p.lastName, a.scheduledDateTime
    """)

    return render_template('analytics/dashboard.html',
                           q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6, q7=q7)
