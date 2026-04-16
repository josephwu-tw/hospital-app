-- ============================================================
-- CS5200 Database Management | Group 10
-- Intelligent Hospital Resource and Queue Management System
-- dbSQL.sql: Analytical Query Script
-- ============================================================

USE hospital_db;

-- ============================================================
-- Query 1 (JOIN — 3 tables)
-- Retrieve all patients currently waiting in the queue,
-- showing their name, department, queue position, and arrival time
-- ============================================================
/*
Expected Output:
personID | firstName | lastName | deptName     | queuePos | arrivalTime         | queueStatus
---------|-----------|----------|--------------|----------|---------------------|------------
1        | Alice     | Chen     | Orthopedics  | 1        | 2024-10-05 07:55:00 | Waiting
2        | Bob       | Wang     | Neurology    | 2        | 2024-10-06 12:45:00 | Waiting
*/
SELECT
    p.personID,
    p.firstName,
    p.lastName,
    d.deptName,
    q.queuePos,
    q.arrivalTime,
    q.queueStatus
FROM Queue q
JOIN Appointment  a ON q.appointmentID = a.appointmentID
JOIN Room         r ON a.roomID        = r.roomID
JOIN Department   d ON r.deptID        = d.deptID
JOIN Person       p ON a.patientID     = p.personID
WHERE q.queueStatus = 'Waiting'
ORDER BY q.arrivalTime;


-- ============================================================
-- Query 2 (AGGREGATE — GROUP BY + HAVING + ORDER BY)
-- Calculate average wait duration per department,
-- only showing departments with average wait > 10 minutes
-- ============================================================
/*
Expected Output (based on sample data):
deptName     | avgWaitMinutes
-------------|---------------
Orthopedics  | 25.00
Neurology    | 22.50
Cardiology   | 16.67
*/
SELECT
    d.deptName,
    ROUND(AVG(TIMESTAMPDIFF(MINUTE, q.arrivalTime, q.calledTime)), 2) AS avgWaitMinutes
FROM Queue q
JOIN Appointment a ON q.appointmentID = a.appointmentID
JOIN Room        r ON a.roomID        = r.roomID
JOIN Department  d ON r.deptID        = d.deptID
WHERE q.calledTime IS NOT NULL
GROUP BY d.deptName
HAVING avgWaitMinutes > 10
ORDER BY avgWaitMinutes DESC;


-- ============================================================
-- Query 3 (AGGREGATE — GROUP BY + HAVING + ORDER BY)
-- List doctors with their total appointment count and
-- average billing amount, only for those with 2+ appointments
-- ============================================================
/*
Expected Output (based on sample data):
doctorID | firstName | lastName | totalAppointments | avgBillingAmount
---------|-----------|----------|-------------------|----------------
6        | Frank     | Lee      | 4                 | 325.00
7        | Grace     | Park     | 3                 | 223.33
8        | Henry     | Zhao     | 3                 | 298.33
*/
SELECT
    doc.personID                                AS doctorID,
    p.firstName,
    p.lastName,
    COUNT(a.appointmentID)                      AS totalAppointments,
    ROUND(AVG(b.totalAmount), 2)                AS avgBillingAmount
FROM Doctor doc
JOIN Person      p  ON doc.personID     = p.personID
JOIN Appointment a  ON doc.personID     = a.doctorID
JOIN Billing     b  ON a.appointmentID  = b.appointmentID
GROUP BY doc.personID, p.firstName, p.lastName
HAVING totalAppointments >= 2
ORDER BY totalAppointments DESC;


-- ============================================================
-- Query 4 (SUBQUERY — inline view / WITH clause)
-- Find patients who waited 30 minutes or more
-- beyond their scheduled appointment time
-- ============================================================
/*
Expected Output (based on sample data — waitMinutes >= 30):
patientID | firstName | lastName | appointmentID | scheduledDateTime   | waitMinutes
----------|-----------|----------|---------------|---------------------|------------
5         | Eva       | Wu       | 5             | 2024-10-03 14:00:00 | 30
*/
WITH late_waits AS (
    SELECT
        a.patientID,
        a.appointmentID,
        a.scheduledDateTime,
        TIMESTAMPDIFF(MINUTE, q.arrivalTime, q.calledTime) AS waitMinutes
    FROM Queue q
    JOIN Appointment a ON q.appointmentID = a.appointmentID
    WHERE q.calledTime IS NOT NULL
)
SELECT
    lw.patientID,
    p.firstName,
    p.lastName,
    lw.appointmentID,
    lw.scheduledDateTime,
    lw.waitMinutes
FROM late_waits lw
JOIN Person p ON lw.patientID = p.personID
WHERE lw.waitMinutes >= 30
ORDER BY lw.waitMinutes DESC;


-- ============================================================
-- Query 5 (JOIN — multi-table)
-- Retrieve all unpaid billing records older than 30 days,
-- including patient name and doctor name
-- ============================================================
/*
Expected Output (all Oct 2024 dates are >30 days old, 4 unpaid records returned):
billingID | patientName  | doctorName  | totalAmount | billingDate | daysOverdue
----------|--------------|-------------|-------------|-------------|------------
4         | David Kim    | Henry Zhao  | 400.00      | 2024-10-02  | (varies)
6         | Alice Chen   | Henry Zhao  | 220.00      | 2024-10-05  | (varies)
7         | Bob Wang     | Grace Park  | 190.00      | 2024-10-06  | (varies)
8         | Carol Lin    | Frank Lee   | 350.00      | 2024-10-07  | (varies)
*/
SELECT
    b.billingID,
    CONCAT(pat_p.firstName, ' ', pat_p.lastName)  AS patientName,
    CONCAT(doc_p.firstName, ' ', doc_p.lastName)  AS doctorName,
    b.totalAmount,
    b.billingDate,
    DATEDIFF(CURDATE(), b.billingDate)             AS daysOverdue
FROM Billing b
JOIN Appointment a   ON b.appointmentID = a.appointmentID
JOIN Person pat_p    ON a.patientID     = pat_p.personID
JOIN Person doc_p    ON a.doctorID      = doc_p.personID
WHERE b.paymentStatus = 'Unpaid'
  AND b.billingDate < DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY daysOverdue DESC;


-- ============================================================
-- Query 6 (JOIN — 4 tables + subquery)
-- Find appointments that were canceled or rescheduled
-- more than once, with patient and doctor details
-- ============================================================
/*
Expected Output:
appointmentID | patientName | doctorName   | status       | rescheduleCount | scheduledDateTime
--------------|-------------|--------------|--------------|-----------------|-------------------
4             | David Kim   | Henry Zhao   | Canceled     | 2               | 2024-10-02 11:00:00
8             | Carol Lin   | Frank Lee    | Rescheduled  | 2               | 2024-10-07 15:00:00
*/
SELECT
    a.appointmentID,
    CONCAT(pat.firstName, ' ', pat.lastName)  AS patientName,
    CONCAT(doc.firstName, ' ', doc.lastName)  AS doctorName,
    a.status,
    a.rescheduleCount,
    a.scheduledDateTime
FROM Appointment a
JOIN Person pat ON a.patientID = pat.personID
JOIN Person doc ON a.doctorID  = doc.personID
WHERE (a.status = 'Canceled' OR a.status = 'Rescheduled')
  AND a.rescheduleCount > 1
ORDER BY a.rescheduleCount DESC;


-- ============================================================
-- Query 7 (JOIN + AGGREGATE — complete treatment history)
-- Retrieve full treatment history for a specific patient
-- (patientID = 1), including device usage
-- ============================================================
/*
Expected Output:
appointmentID | scheduledDateTime   | diagnosis        | deviceName  | usagePurpose
--------------|---------------------|------------------|-------------|----------------------------
1             | 2024-10-01 09:00:00 | Hypertension ... | ECG Monitor | ECG for hypertension baseline
*/
SELECT
    a.appointmentID,
    a.scheduledDateTime,
    mr.diagnosis,
    mr.treatmentPlan,
    mr.prescriptions,
    md.deviceName,
    rd.usagePurpose
FROM Appointment  a
JOIN MedicalRecord mr ON a.appointmentID  = mr.appointmentID
LEFT JOIN Record_Device rd ON mr.recordID = rd.recordID
LEFT JOIN MedicalDevice md ON rd.deviceID = md.deviceID
WHERE a.patientID = 1
ORDER BY a.scheduledDateTime;