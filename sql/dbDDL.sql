-- ============================================================
-- CS5200 Database Management | Group 10
-- Intelligent Hospital Resource and Queue Management System
-- dbDDL.sql: Schema Creation Script
-- ============================================================

CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- ------------------------------------------------------------
-- TABLE: Person (Superclass)
-- ------------------------------------------------------------
CREATE TABLE Person (
    personID      INT           NOT NULL AUTO_INCREMENT,
    firstName     VARCHAR(50)   NOT NULL,
    lastName      VARCHAR(50)   NOT NULL,
    dateOfBirth   DATE          NOT NULL,
    phone         VARCHAR(20)   UNIQUE,
    email         VARCHAR(100)  UNIQUE,
    address       VARCHAR(255),
    PRIMARY KEY (personID)
);

-- ------------------------------------------------------------
-- TABLE: Department
-- ------------------------------------------------------------
CREATE TABLE Department (
    deptID        INT           NOT NULL AUTO_INCREMENT,
    deptName      VARCHAR(100)  NOT NULL UNIQUE,
    location      VARCHAR(100),
    phone         VARCHAR(20),
    PRIMARY KEY (deptID)
);

-- ------------------------------------------------------------
-- TABLE: Patient (Subclass of Person)
-- ------------------------------------------------------------
CREATE TABLE Patient (
    personID         INT          NOT NULL,
    bloodType        VARCHAR(5),
    allergies        VARCHAR(255),
    emergencyContact VARCHAR(100),
    PRIMARY KEY (personID),
    FOREIGN KEY (personID) REFERENCES Person(personID) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- TABLE: Staff (Subclass of Person)
-- ------------------------------------------------------------
CREATE TABLE Staff (
    personID    INT            NOT NULL,
    employeeID  VARCHAR(20)    NOT NULL UNIQUE,
    hireDate    DATE           NOT NULL,
    salary      DECIMAL(10,2)  NOT NULL,
    PRIMARY KEY (personID),
    FOREIGN KEY (personID) REFERENCES Person(personID) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- TABLE: Doctor (Subclass of Staff)
-- ------------------------------------------------------------
CREATE TABLE Doctor (
    personID        INT          NOT NULL,
    licenseNumber   VARCHAR(50)  NOT NULL UNIQUE,
    specialization  VARCHAR(100),
    yearsExperience INT,
    deptID          INT          NOT NULL,
    PRIMARY KEY (personID),
    FOREIGN KEY (personID) REFERENCES Staff(personID) ON DELETE CASCADE,
    FOREIGN KEY (deptID)   REFERENCES Department(deptID)
);

-- ------------------------------------------------------------
-- TABLE: Nurse (Subclass of Staff)
-- ------------------------------------------------------------
CREATE TABLE Nurse (
    personID    INT          NOT NULL,
    certNumber  VARCHAR(50)  NOT NULL UNIQUE,
    nurseLevel  VARCHAR(50),
    PRIMARY KEY (personID),
    FOREIGN KEY (personID) REFERENCES Staff(personID) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- TABLE: Nurse_Department (N:M — ASSIGNED_TO)
-- ------------------------------------------------------------
CREATE TABLE Nurse_Department (
    personID   INT          NOT NULL,
    deptID     INT          NOT NULL,
    startDate  DATE         NOT NULL,
    role       VARCHAR(50),
    PRIMARY KEY (personID, deptID),
    FOREIGN KEY (personID) REFERENCES Nurse(personID)      ON DELETE CASCADE,
    FOREIGN KEY (deptID)   REFERENCES Department(deptID)   ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- TABLE: Room
-- ------------------------------------------------------------
CREATE TABLE Room (
    roomID      INT          NOT NULL AUTO_INCREMENT,
    roomNumber  VARCHAR(20)  NOT NULL UNIQUE,
    roomType    VARCHAR(50),
    floor       INT,
    capacity    INT,
    status      VARCHAR(20)  DEFAULT 'Available',
    deptID      INT          NOT NULL,
    PRIMARY KEY (roomID),
    FOREIGN KEY (deptID) REFERENCES Department(deptID)
);

-- ------------------------------------------------------------
-- TABLE: Insurance
-- ------------------------------------------------------------
CREATE TABLE Insurance (
    insuranceID      INT            NOT NULL AUTO_INCREMENT,
    providerName     VARCHAR(100)   NOT NULL,
    policyNumber     VARCHAR(50)    NOT NULL UNIQUE,
    coverageAmount   DECIMAL(12,2),
    expiryDate       DATE,
    PRIMARY KEY (insuranceID)
);

-- ------------------------------------------------------------
-- TABLE: Patient_Insurance (N:M — HOLDS)
-- ------------------------------------------------------------
CREATE TABLE Patient_Insurance (
    personID        INT   NOT NULL,
    insuranceID     INT   NOT NULL,
    enrollmentDate  DATE,
    PRIMARY KEY (personID, insuranceID),
    FOREIGN KEY (personID)    REFERENCES Patient(personID)     ON DELETE CASCADE,
    FOREIGN KEY (insuranceID) REFERENCES Insurance(insuranceID) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- TABLE: Appointment
-- ------------------------------------------------------------
CREATE TABLE Appointment (
    appointmentID        INT           NOT NULL AUTO_INCREMENT,
    scheduledDateTime    DATETIME      NOT NULL,
    actualStartTime      DATETIME,
    status               VARCHAR(30)   DEFAULT 'Scheduled',
    rescheduleCount      INT           DEFAULT 0,
    appointmentType      VARCHAR(50),
    patientID            INT           NOT NULL,
    doctorID             INT           NOT NULL,
    roomID               INT,
    PRIMARY KEY (appointmentID),
    FOREIGN KEY (patientID) REFERENCES Patient(personID),
    FOREIGN KEY (doctorID)  REFERENCES Doctor(personID),
    FOREIGN KEY (roomID)    REFERENCES Room(roomID)
);

-- ------------------------------------------------------------
-- TABLE: Queue (Weak Entity — depends on Appointment)
-- ------------------------------------------------------------
CREATE TABLE Queue (
    appointmentID  INT          NOT NULL,
    queuePos       INT          NOT NULL,
    arrivalTime    DATETIME     NOT NULL,
    calledTime     DATETIME,
    queueStatus    VARCHAR(30)  DEFAULT 'Waiting',
    -- Derived: waitDuration = TIMESTAMPDIFF(MINUTE, arrivalTime, calledTime)
    PRIMARY KEY (appointmentID, queuePos),
    FOREIGN KEY (appointmentID) REFERENCES Appointment(appointmentID) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- TABLE: MedicalRecord
-- ------------------------------------------------------------
CREATE TABLE MedicalRecord (
    recordID       INT           NOT NULL AUTO_INCREMENT,
    diagnosis      VARCHAR(255),
    treatmentPlan  TEXT,
    prescriptions  TEXT,
    labResults     TEXT,
    recordDate     DATE          NOT NULL,
    appointmentID  INT           NOT NULL UNIQUE,  -- 1:1 with Appointment
    PRIMARY KEY (recordID),
    FOREIGN KEY (appointmentID) REFERENCES Appointment(appointmentID)
);

-- ------------------------------------------------------------
-- TABLE: MedicalDevice
-- ------------------------------------------------------------
CREATE TABLE MedicalDevice (
    deviceID              INT          NOT NULL AUTO_INCREMENT,
    deviceName            VARCHAR(100) NOT NULL,
    deviceType            VARCHAR(50),
    serialNumber          VARCHAR(100) NOT NULL UNIQUE,
    lastMaintenanceDate   DATE,
    status                VARCHAR(30)  DEFAULT 'Available',
    PRIMARY KEY (deviceID)
);

-- ------------------------------------------------------------
-- TABLE: Record_Device (N:M — USES)
-- ------------------------------------------------------------
CREATE TABLE Record_Device (
    recordID      INT           NOT NULL,
    deviceID      INT           NOT NULL,
    usageDate     DATE          NOT NULL,
    duration      DECIMAL(6,2),  -- in hours
    usagePurpose  VARCHAR(255),
    PRIMARY KEY (recordID, deviceID, usageDate),
    FOREIGN KEY (recordID)  REFERENCES MedicalRecord(recordID) ON DELETE CASCADE,
    FOREIGN KEY (deviceID)  REFERENCES MedicalDevice(deviceID)
);

-- ------------------------------------------------------------
-- TABLE: Billing
-- ------------------------------------------------------------
CREATE TABLE Billing (
    billingID      INT            NOT NULL AUTO_INCREMENT,
    totalAmount    DECIMAL(12,2)  NOT NULL,
    amountPaid     DECIMAL(12,2)  DEFAULT 0.00,
    billingDate    DATE           NOT NULL,
    dueDate        DATE,
    paymentStatus  VARCHAR(30)    DEFAULT 'Unpaid',
    appointmentID  INT            NOT NULL UNIQUE,  -- 1:1 with Appointment
    insuranceID    INT,                             -- nullable
    PRIMARY KEY (billingID),
    FOREIGN KEY (appointmentID) REFERENCES Appointment(appointmentID),
    FOREIGN KEY (insuranceID)   REFERENCES Insurance(insuranceID)
);

-- ============================================================
-- VIEW: v_waiting_patients
-- Shows all patients currently in 'Waiting' status with dept
-- ============================================================
CREATE OR REPLACE VIEW v_waiting_patients AS
SELECT
    p.personID,
    p.firstName,
    p.lastName,
    d.deptName,
    q.queuePos,
    q.arrivalTime,
    q.queueStatus
FROM Queue q
JOIN Appointment a  ON q.appointmentID = a.appointmentID
JOIN Room r         ON a.roomID = r.roomID
JOIN Department d   ON r.deptID = d.deptID
JOIN Person p       ON a.patientID = p.personID
WHERE q.queueStatus = 'Waiting';

-- ============================================================
-- INDEX: Speed up common lookups
-- ============================================================
CREATE INDEX idx_appt_patient   ON Appointment(patientID);
CREATE INDEX idx_appt_doctor    ON Appointment(doctorID);
CREATE INDEX idx_appt_status    ON Appointment(status);
CREATE INDEX idx_queue_status   ON Queue(queueStatus);
CREATE INDEX idx_billing_status ON Billing(paymentStatus);
CREATE INDEX idx_device_status  ON MedicalDevice(status);

-- ============================================================
-- TRIGGER: trg_after_appointment_insert
-- Automatically creates a Billing record when a new
-- Appointment is inserted (default Unpaid, amount TBD as 0)
-- ============================================================
DELIMITER $$

CREATE TRIGGER trg_after_appointment_insert
AFTER INSERT ON Appointment
FOR EACH ROW
BEGIN
    -- Guard prevents duplicate key error if DML is re-run on an existing dataset
    IF NOT EXISTS (SELECT 1 FROM Billing WHERE appointmentID = NEW.appointmentID) THEN
        INSERT INTO Billing (totalAmount, amountPaid, billingDate, dueDate, paymentStatus, appointmentID)
        VALUES (
            0.00,
            0.00,
            DATE(NEW.scheduledDateTime),
            DATE_ADD(DATE(NEW.scheduledDateTime), INTERVAL 30 DAY),
            'Unpaid',
            NEW.appointmentID
        );
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- FUNCTION: fn_wait_duration(appointmentID, queuePos)
-- Returns wait duration in minutes for a given queue entry
-- ============================================================
DELIMITER $$

CREATE FUNCTION fn_wait_duration(p_appointmentID INT, p_queuePos INT)
RETURNS INT
NOT DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_arrival  DATETIME;
    DECLARE v_called   DATETIME;
    DECLARE v_duration INT;

    SELECT arrivalTime, calledTime
    INTO   v_arrival, v_called
    FROM   Queue
    WHERE  appointmentID = p_appointmentID AND queuePos = p_queuePos;

    IF v_called IS NULL THEN
        SET v_duration = TIMESTAMPDIFF(MINUTE, v_arrival, NOW());
    ELSE
        SET v_duration = TIMESTAMPDIFF(MINUTE, v_arrival, v_called);
    END IF;

    RETURN v_duration;
END$$

DELIMITER ;

-- ============================================================
-- PROCEDURE: sp_complete_appointment
-- Marks an appointment as Completed, sets actualStartTime,
-- and updates the queue entry to 'Served'
-- ============================================================
DELIMITER $$

CREATE PROCEDURE sp_complete_appointment(
    IN p_appointmentID INT,
    IN p_actualStart   DATETIME
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    UPDATE Appointment
    SET    status = 'Completed',
           actualStartTime = p_actualStart
    WHERE  appointmentID = p_appointmentID;

    UPDATE Queue
    SET    queueStatus = 'Served',
           calledTime  = p_actualStart
    WHERE  appointmentID = p_appointmentID;

    COMMIT;
END$$

DELIMITER ;
