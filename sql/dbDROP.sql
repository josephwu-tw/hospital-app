-- ============================================================
-- CS5200 Database Management | Group 10
-- Intelligent Hospital Resource and Queue Management System
-- dbDROP.sql: Clean Drop Script
-- ============================================================

USE hospital_db;

-- Disable FK checks so tables can be dropped in any order
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- Drop Triggers
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_after_appointment_insert;

-- ------------------------------------------------------------
-- Drop Views
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_waiting_patients;

-- ------------------------------------------------------------
-- Drop Indexes (non-PK indexes only)
-- ------------------------------------------------------------
ALTER TABLE Appointment  DROP INDEX IF EXISTS idx_appt_patient;
ALTER TABLE Appointment  DROP INDEX IF EXISTS idx_appt_doctor;
ALTER TABLE Appointment  DROP INDEX IF EXISTS idx_appt_status;
ALTER TABLE Queue        DROP INDEX IF EXISTS idx_queue_status;
ALTER TABLE Billing      DROP INDEX IF EXISTS idx_billing_status;
ALTER TABLE MedicalDevice DROP INDEX IF EXISTS idx_device_status;

-- ------------------------------------------------------------
-- Drop Procedures and Functions
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_complete_appointment;
DROP FUNCTION  IF EXISTS fn_wait_duration;

-- ------------------------------------------------------------
-- Drop Tables (leaf → root order)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS Record_Device;
DROP TABLE IF EXISTS Billing;
DROP TABLE IF EXISTS MedicalRecord;
DROP TABLE IF EXISTS Queue;
DROP TABLE IF EXISTS Appointment;
DROP TABLE IF EXISTS Patient_Insurance;
DROP TABLE IF EXISTS Nurse_Department;
DROP TABLE IF EXISTS Nurse;
DROP TABLE IF EXISTS Doctor;
DROP TABLE IF EXISTS Staff;
DROP TABLE IF EXISTS Patient;
DROP TABLE IF EXISTS Room;
DROP TABLE IF EXISTS Insurance;
DROP TABLE IF EXISTS MedicalDevice;
DROP TABLE IF EXISTS Department;
DROP TABLE IF EXISTS Person;

-- Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;
