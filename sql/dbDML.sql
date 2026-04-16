-- ============================================================
-- CS5200 Database Management | Group 10
-- Intelligent Hospital Resource and Queue Management System
-- dbDML.sql: Sample Data Population Script
-- ============================================================

USE hospital_db;

-- ------------------------------------------------------------
-- Person (10 rows)
-- ------------------------------------------------------------
INSERT INTO Person (firstName, lastName, dateOfBirth, phone, email, address) VALUES
('Alice',   'Chen',    '1990-03-15', '617-111-0001', 'alice.chen@email.com',    '10 Maple St, Boston, MA'),
('Bob',     'Wang',    '1985-07-22', '617-111-0002', 'bob.wang@email.com',      '22 Oak Ave, Boston, MA'),
('Carol',   'Lin',     '1978-11-05', '617-111-0003', 'carol.lin@email.com',     '5 Pine Rd, Cambridge, MA'),
('David',   'Kim',     '1965-01-30', '617-111-0004', 'david.kim@email.com',     '88 Elm St, Somerville, MA'),
('Eva',     'Wu',      '1992-06-18', '617-111-0005', 'eva.wu@email.com',        '3 Birch Ln, Brookline, MA'),
('Frank',   'Lee',     '1980-09-09', '617-111-0006', 'frank.lee@email.com',     '77 Cedar Dr, Newton, MA'),
('Grace',   'Park',    '1975-04-25', '617-111-0007', 'grace.park@email.com',    '14 Walnut St, Quincy, MA'),
('Henry',   'Zhao',    '1988-12-01', '617-111-0008', 'henry.zhao@email.com',    '31 Spruce Ave, Waltham, MA'),
('Iris',    'Huang',   '1995-08-14', '617-111-0009', 'iris.huang@email.com',    '9 Willow Ct, Malden, MA'),
('James',   'Smith',   '1970-02-28', '617-111-0010', 'james.smith@email.com',   '55 Ash Blvd, Medford, MA');

-- ------------------------------------------------------------
-- Department (8 rows)
-- ------------------------------------------------------------
INSERT INTO Department (deptName, location, phone) VALUES
('Cardiology',       'Building A, Floor 2', '617-200-0001'),
('Neurology',        'Building A, Floor 3', '617-200-0002'),
('Orthopedics',      'Building B, Floor 1', '617-200-0003'),
('Radiology',        'Building B, Floor 2', '617-200-0004'),
('Emergency',        'Building C, Floor 1', '617-200-0005'),
('Oncology',         'Building D, Floor 2', '617-200-0006'),
('Pediatrics',       'Building E, Floor 1', '617-200-0007'),
('General Surgery',  'Building F, Floor 3', '617-200-0008');

-- ------------------------------------------------------------
-- Patient (persons 1–5 are patients)
-- ------------------------------------------------------------
INSERT INTO Patient (personID, bloodType, allergies, emergencyContact) VALUES
(1, 'A+',  'Penicillin',       'John Chen: 617-999-0001'),
(2, 'O-',  'None',             'Mary Wang: 617-999-0002'),
(3, 'B+',  'Aspirin, Latex',   'Tom Lin: 617-999-0003'),
(4, 'AB+', 'None',             'Sue Kim: 617-999-0004'),
(5, 'O+',  'Sulfa drugs',      'Leo Wu: 617-999-0005');

-- ------------------------------------------------------------
-- Staff (persons 6–10 are staff)
-- ------------------------------------------------------------
INSERT INTO Staff (personID, employeeID, hireDate, salary) VALUES
(6,  'EMP-001', '2015-06-01', 180000.00),
(7,  'EMP-002', '2018-03-15', 175000.00),
(8,  'EMP-003', '2020-09-01', 165000.00),
(9,  'EMP-004', '2019-07-20', 72000.00),
(10, 'EMP-005', '2017-11-10', 68000.00);

-- ------------------------------------------------------------
-- Doctor (persons 6–8 are doctors)
-- ------------------------------------------------------------
INSERT INTO Doctor (personID, licenseNumber, specialization, yearsExperience, deptID) VALUES
(6, 'LIC-101', 'Cardiology',  15, 1),
(7, 'LIC-102', 'Neurology',   12, 2),
(8, 'LIC-103', 'Orthopedics',  8, 3);

-- ------------------------------------------------------------
-- Nurse (persons 9–10 are nurses)
-- ------------------------------------------------------------
INSERT INTO Nurse (personID, certNumber, nurseLevel) VALUES
(9,  'CERT-201', 'RN'),
(10, 'CERT-202', 'NP');

-- ------------------------------------------------------------
-- Nurse_Department
-- ------------------------------------------------------------
INSERT INTO Nurse_Department (personID, deptID, startDate, role) VALUES
(9,  1, '2019-07-20', 'Head Nurse'),
(9,  5, '2021-01-01', 'Rotation Nurse'),
(10, 2, '2017-11-10', 'Nurse Practitioner');

-- ------------------------------------------------------------
-- Room (10 rows)
-- ------------------------------------------------------------
INSERT INTO Room (roomNumber, roomType, floor, capacity, status, deptID) VALUES
('A201', 'Consultation', 2, 1, 'Available', 1),
('A202', 'Consultation', 2, 1, 'Available', 1),
('A301', 'Consultation', 3, 1, 'Available', 2),
('B101', 'Procedure',    1, 2, 'Available', 3),
('B201', 'Imaging',      2, 1, 'Available', 4),
('C101', 'Emergency',    1, 4, 'Occupied',  5),
('D201', 'Treatment',    2, 2, 'Available', 6),
('E101', 'Pediatric',    1, 2, 'Available', 7),
('F301', 'Operating',    3, 5, 'Available', 8),
('A203', 'Recovery',     2, 3, 'Available', 1);

-- ------------------------------------------------------------
-- Insurance (8 rows)
-- ------------------------------------------------------------
INSERT INTO Insurance (providerName, policyNumber, coverageAmount, expiryDate) VALUES
('BlueCross BlueShield', 'POL-001', 100000.00, '2026-12-31'),
('Aetna',                'POL-002',  80000.00, '2025-06-30'),
('Cigna',                'POL-003',  90000.00, '2026-03-31'),
('United Health',        'POL-004', 120000.00, '2027-01-01'),
('Humana',               'POL-005',  75000.00, '2025-09-30'),
('Harvard Pilgrim',      'POL-006',  95000.00, '2026-08-15'),
('Tufts Health',         'POL-007', 110000.00, '2027-06-01'),
('Mass General Brigham', 'POL-008',  85000.00, '2025-12-31');

-- ------------------------------------------------------------
-- Patient_Insurance
-- ------------------------------------------------------------
INSERT INTO Patient_Insurance (personID, insuranceID, enrollmentDate) VALUES
(1, 1, '2022-01-01'),
(2, 2, '2021-06-15'),
(3, 3, '2020-03-10'),
(4, 4, '2023-01-01'),
(5, 5, '2022-09-01'),
(1, 6, '2023-07-01'),
(3, 7, '2024-01-15');

-- ------------------------------------------------------------
-- Appointment (10 rows)
-- NOTE: Billing rows auto-created via trigger
-- ------------------------------------------------------------
INSERT INTO Appointment (scheduledDateTime, actualStartTime, status, rescheduleCount, appointmentType, patientID, doctorID, roomID) VALUES
('2024-10-01 09:00:00', '2024-10-01 09:10:00', 'Completed',  0, 'Checkup',    1, 6, 1),
('2024-10-01 10:00:00', '2024-10-01 10:15:00', 'Completed',  1, 'Follow-up',  2, 6, 2),
('2024-10-02 09:30:00', '2024-10-02 09:35:00', 'Completed',  0, 'Checkup',    3, 7, 3),
('2024-10-02 11:00:00', NULL,                  'Canceled',   2, 'Procedure',  4, 8, 4),
('2024-10-03 14:00:00', '2024-10-03 14:20:00', 'Completed',  0, 'Checkup',    5, 7, 3),
('2024-10-05 08:00:00', NULL,                  'Scheduled',  0, 'Checkup',    1, 8, 4),
('2024-10-06 13:00:00', NULL,                  'Scheduled',  1, 'Follow-up',  2, 7, 3),
('2024-10-07 15:00:00', NULL,                  'Rescheduled',2, 'Procedure',  3, 6, 1),
('2024-10-08 09:00:00', '2024-10-08 09:05:00', 'Completed',  0, 'Emergency',  4, 6, 2),
('2024-10-09 10:30:00', '2024-10-09 10:45:00', 'Completed',  0, 'Checkup',    5, 8, 4);

-- ------------------------------------------------------------
-- Queue (one entry per completed/active appointment)
-- ------------------------------------------------------------
INSERT INTO Queue (appointmentID, queuePos, arrivalTime, calledTime, queueStatus) VALUES
(1,  1, '2024-10-01 08:50:00', '2024-10-01 09:10:00', 'Served'),
(2,  2, '2024-10-01 09:55:00', '2024-10-01 10:15:00', 'Served'),
(3,  1, '2024-10-02 09:20:00', '2024-10-02 09:35:00', 'Served'),
(5,  1, '2024-10-03 13:50:00', '2024-10-03 14:20:00', 'Served'),
(6,  1, '2024-10-05 07:55:00', NULL,                  'Waiting'),
(7,  2, '2024-10-06 12:45:00', NULL,                  'Waiting'),
(9,  1, '2024-10-08 08:55:00', '2024-10-08 09:05:00', 'Served'),
(10, 1, '2024-10-09 10:20:00', '2024-10-09 10:45:00', 'Served');

-- ------------------------------------------------------------
-- MedicalRecord (one per completed appointment)
-- ------------------------------------------------------------
INSERT INTO MedicalRecord (diagnosis, treatmentPlan, prescriptions, labResults, recordDate, appointmentID) VALUES
('Hypertension Stage 1',       'Lifestyle changes, monitor BP weekly',    'Lisinopril 10mg daily',    'BP: 145/92',   '2024-10-01', 1),
('Hypertension follow-up',     'Continue medication, reduce sodium',      'Lisinopril 10mg daily',    'BP: 138/88',   '2024-10-01', 2),
('Migraine disorder',          'Avoid triggers, rest in dark room',       'Sumatriptan 50mg PRN',     'MRI: Normal',  '2024-10-02', 3),
('Anxiety disorder',           'CBT therapy, relaxation techniques',      'Escitalopram 10mg daily',  'NAD',          '2024-10-03', 5),
('Chest pain, ruled out ACS',  'EKG monitoring, follow-up in 2 weeks',    'Aspirin 81mg daily',       'EKG: Normal',  '2024-10-08', 9),
('Knee osteoarthritis',        'Physical therapy, weight management',     'Ibuprofen 400mg PRN',      'X-Ray: Grade 2 OA', '2024-10-09', 10);

-- ------------------------------------------------------------
-- MedicalDevice (8 rows)
-- ------------------------------------------------------------
INSERT INTO MedicalDevice (deviceName, deviceType, serialNumber, lastMaintenanceDate, status) VALUES
('MRI Machine',       'Imaging',      'SN-MRI-001', '2024-08-01', 'Available'),
('CT Scanner',        'Imaging',      'SN-CT-001',  '2024-07-15', 'Available'),
('X-Ray Machine',     'Imaging',      'SN-XR-001',  '2024-09-01', 'Available'),
('ECG Monitor',       'Monitoring',   'SN-ECG-001', '2024-09-10', 'In Use'),
('Ultrasound',        'Imaging',      'SN-US-001',  '2024-08-20', 'Available'),
('Ventilator',        'Life Support', 'SN-VN-001',  '2024-06-30', 'Available'),
('Blood Analyzer',    'Lab',          'SN-BA-001',  '2024-09-05', 'Available'),
('Defibrillator',     'Emergency',    'SN-DF-001',  '2024-07-01', 'Available');

-- ------------------------------------------------------------
-- Record_Device
-- ------------------------------------------------------------
INSERT INTO Record_Device (recordID, deviceID, usageDate, duration, usagePurpose) VALUES
(1, 4, '2024-10-01', 0.25, 'ECG for hypertension baseline'),
(2, 4, '2024-10-01', 0.25, 'ECG follow-up'),
(3, 1, '2024-10-02', 0.75, 'Brain MRI for migraine workup'),
(5, 4, '2024-10-08', 0.50, 'ECG for chest pain evaluation'),
(6, 3, '2024-10-09', 0.30, 'Knee X-Ray for osteoarthritis'),
(4, 7, '2024-10-03', 0.20, 'Blood panel for anxiety baseline');

-- ------------------------------------------------------------
-- UPDATE Billing (set amounts for completed appointments)
-- Trigger created rows with 0.00 — we update them here
-- ------------------------------------------------------------
UPDATE Billing SET totalAmount = 250.00, amountPaid = 250.00, paymentStatus = 'Paid'    WHERE appointmentID = 1;
UPDATE Billing SET totalAmount = 200.00, amountPaid = 200.00, paymentStatus = 'Paid'    WHERE appointmentID = 2;
UPDATE Billing SET totalAmount = 300.00, amountPaid = 150.00, paymentStatus = 'Partial' WHERE appointmentID = 3;
UPDATE Billing SET totalAmount = 400.00, amountPaid = 0.00,   paymentStatus = 'Unpaid'  WHERE appointmentID = 4;
UPDATE Billing SET totalAmount = 180.00, amountPaid = 180.00, paymentStatus = 'Paid'    WHERE appointmentID = 5;
UPDATE Billing SET totalAmount = 220.00, amountPaid = 0.00,   paymentStatus = 'Unpaid'  WHERE appointmentID = 6;
UPDATE Billing SET totalAmount = 190.00, amountPaid = 0.00,   paymentStatus = 'Unpaid'  WHERE appointmentID = 7;
UPDATE Billing SET totalAmount = 350.00, amountPaid = 0.00,   paymentStatus = 'Unpaid'  WHERE appointmentID = 8;
UPDATE Billing SET totalAmount = 500.00, amountPaid = 500.00, paymentStatus = 'Paid'    WHERE appointmentID = 9;
UPDATE Billing SET totalAmount = 275.00, amountPaid = 275.00, paymentStatus = 'Paid'    WHERE appointmentID = 10;

-- Link insurance to some billing records
UPDATE Billing SET insuranceID = 1 WHERE appointmentID IN (1, 6);
UPDATE Billing SET insuranceID = 2 WHERE appointmentID = 2;
UPDATE Billing SET insuranceID = 3 WHERE appointmentID = 3;
UPDATE Billing SET insuranceID = 5 WHERE appointmentID IN (5, 10);
