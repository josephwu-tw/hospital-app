from flask import Blueprint, render_template
from db import execute_query

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics')
def dashboard():
    # Q1 — patients currently waiting in queue
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

    # Q2 — average wait time per department (> 10 min)
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

    # Q3 — doctors with highest appointments in past month
    q3 = execute_query("""
        SELECT doc.personID AS doctorID, p.firstName, p.lastName,
               d.deptName, COUNT(a.appointmentID) AS apptCount
        FROM Doctor doc
        JOIN Person      p    ON doc.personID = p.personID
        JOIN Department  d    ON doc.deptID   = d.deptID
        JOIN Appointment a    ON doc.personID = a.doctorID
        WHERE a.scheduledDateTime >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY doc.personID, p.firstName, p.lastName, d.deptName
        ORDER BY apptCount DESC
    """)

    # Q4 — medical devices with utilization > 90% (past 30 days)
    q4 = execute_query("""
        SELECT md.deviceID, md.deviceName, md.deviceType,
               ROUND(SUM(rd.duration) / 720.0 * 100, 1) AS utilizationPct
        FROM Record_Device rd
        JOIN MedicalDevice md ON rd.deviceID = md.deviceID
        WHERE rd.usageDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY md.deviceID, md.deviceName, md.deviceType
        HAVING utilizationPct > 90
        ORDER BY utilizationPct DESC
    """)

    # Q5 — appointments canceled or rescheduled more than once
    q5 = execute_query("""
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

    # Q6 — full treatment history for all patients
    q6 = execute_query("""
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

    # Q7 — peak hours by patient arrival
    q7 = execute_query("""
        SELECT HOUR(q.arrivalTime) AS hourSlot,
               COUNT(*) AS patientCount
        FROM Queue q
        GROUP BY HOUR(q.arrivalTime)
        ORDER BY patientCount DESC
    """)

    # Q8 — patients who waited 30+ minutes beyond scheduled time
    q8 = execute_query("""
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

    # Q9 — average consultation duration per doctor
    q9 = execute_query("""
        SELECT doc.personID AS doctorID, p.firstName, p.lastName,
               ROUND(AVG(TIMESTAMPDIFF(MINUTE, a.scheduledDateTime, a.actualStartTime)), 2) AS avgLagMinutes,
               COUNT(a.appointmentID) AS completedCount
        FROM Doctor doc
        JOIN Person      p ON doc.personID = p.personID
        JOIN Appointment a ON doc.personID = a.doctorID
        WHERE a.status = 'Completed'
          AND a.actualStartTime IS NOT NULL
        GROUP BY doc.personID, p.firstName, p.lastName
        ORDER BY avgLagMinutes
    """)

    # Q10 — departments with highest patient volume
    q10 = execute_query("""
        SELECT d.deptID, d.deptName, COUNT(a.appointmentID) AS volume
        FROM Department  d
        JOIN Room        r ON r.deptID        = d.deptID
        JOIN Appointment a ON a.roomID        = r.roomID
        GROUP BY d.deptID, d.deptName
        ORDER BY volume DESC
    """)

    # Q11 — unpaid billing records older than 30 days
    q11 = execute_query("""
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

    # Q12 — patients visited 5+ times in last year
    q12 = execute_query("""
        SELECT a.patientID, p.firstName, p.lastName,
               COUNT(a.appointmentID) AS visitCount
        FROM Appointment a
        JOIN Person p ON a.patientID = p.personID
        WHERE a.scheduledDateTime >= DATE_SUB(NOW(), INTERVAL 365 DAY)
          AND a.status = 'Completed'
        GROUP BY a.patientID, p.firstName, p.lastName
        HAVING visitCount > 5
        ORDER BY visitCount DESC
    """)

    # Q13 — medical equipment idle for more than 48 hours
    q13 = execute_query("""
        SELECT md.deviceID, md.deviceName, md.deviceType, md.status,
               MAX(rd.usageDate) AS lastUsed,
               DATEDIFF(CURDATE(), MAX(rd.usageDate)) AS idleDays
        FROM MedicalDevice md
        LEFT JOIN Record_Device rd ON md.deviceID = rd.deviceID
        GROUP BY md.deviceID, md.deviceName, md.deviceType, md.status
        HAVING lastUsed IS NULL OR idleDays > 2
        ORDER BY idleDays DESC
    """)

    # Q14 — daily report: appointments and completed treatments
    q14 = execute_query("""
        SELECT DATE(a.scheduledDateTime) AS reportDate,
               COUNT(a.appointmentID)   AS totalAppointments,
               SUM(a.status = 'Completed') AS completedTreatments
        FROM Appointment a
        GROUP BY DATE(a.scheduledDateTime)
        ORDER BY reportDate DESC
        LIMIT 30
    """)

    # Q15 — avg waiting before vs after a policy date (2025-01-01)
    q15_before = execute_query("""
        SELECT ROUND(AVG(TIMESTAMPDIFF(MINUTE, q.arrivalTime, q.calledTime)), 2) AS avgWaitBefore
        FROM Queue q
        WHERE q.arrivalTime < '2025-01-01'
          AND q.calledTime IS NOT NULL
    """, one=True)

    q15_after = execute_query("""
        SELECT ROUND(AVG(TIMESTAMPDIFF(MINUTE, q.arrivalTime, q.calledTime)), 2) AS avgWaitAfter
        FROM Queue q
        WHERE q.arrivalTime >= '2025-01-01'
          AND q.calledTime IS NOT NULL
    """, one=True)

    q15 = [{
        'before_date': 'Before 2025-01-01',
        'after_date': 'After 2025-01-01',
        'avgWaitBefore': q15_before['avgWaitBefore'] if q15_before else None,
        'avgWaitAfter': q15_after['avgWaitAfter'] if q15_after else None,
    }]

    # Q16 — doctors with highest cancellation rates
    q16 = execute_query("""
        SELECT doc.personID AS doctorID, p.firstName, p.lastName,
               COUNT(a.appointmentID)                                AS totalAppts,
               SUM(a.status = 'Canceled')                           AS canceledAppts,
               ROUND(SUM(a.status = 'Canceled') / COUNT(*) * 100, 1) AS cancelRate
        FROM Doctor doc
        JOIN Person      p ON doc.personID = p.personID
        JOIN Appointment a ON doc.personID = a.doctorID
        GROUP BY doc.personID, p.firstName, p.lastName
        HAVING canceledAppts > 0
        ORDER BY cancelRate DESC
    """)

    return render_template('analytics/dashboard.html',
                           q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6,
                           q7=q7, q8=q8, q9=q9, q10=q10, q11=q11,
                           q12=q12, q13=q13, q14=q14, q15=q15, q16=q16)
