from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

doctors_bp = Blueprint('doctors', __name__)

_LIST_SQL = """
    SELECT d.personID, p.firstName, p.lastName, p.email, p.phone,
           d.licenseNumber, d.specialization, d.yearsExperience,
           dept.deptName, dept.deptID,
           s.employeeID, s.hireDate
    FROM Doctor d
    JOIN Person p      ON d.personID = p.personID
    JOIN Staff  s      ON d.personID = s.personID
    JOIN Department dept ON d.deptID = dept.deptID
    ORDER BY p.lastName, p.firstName
"""

_DETAIL_SQL = """
    SELECT d.personID, p.firstName, p.lastName, p.email, p.phone,
           p.dateOfBirth, p.address,
           d.licenseNumber, d.specialization, d.yearsExperience, d.deptID,
           dept.deptName, s.employeeID, s.hireDate, s.salary
    FROM Doctor d
    JOIN Person p        ON d.personID = p.personID
    JOIN Staff  s        ON d.personID = s.personID
    JOIN Department dept ON d.deptID   = dept.deptID
    WHERE d.personID = %s
"""


@doctors_bp.route('/doctors')
def list_doctors():
    doctors = execute_query(_LIST_SQL)
    return render_template('doctors/list.html', doctors=doctors)


@doctors_bp.route('/doctors/<int:did>')
def view_doctor(did):
    doctor = execute_query(_DETAIL_SQL, (did,), one=True)
    if not doctor:
        flash('Doctor not found.', 'danger')
        return redirect(url_for('doctors.list_doctors'))
    appointments = execute_query(
        """SELECT a.appointmentID, a.scheduledDateTime, a.status, a.appointmentType,
                  CONCAT(p.firstName, ' ', p.lastName) AS patientName
           FROM Appointment a
           JOIN Person p ON a.patientID = p.personID
           WHERE a.doctorID = %s
           ORDER BY a.scheduledDateTime DESC
           LIMIT 20""",
        (did,)
    )
    return render_template('doctors/detail.html', doctor=doctor, appointments=appointments)


@doctors_bp.route('/doctors/new', methods=['GET', 'POST'])
def new_doctor():
    departments = execute_query("SELECT deptID, deptName FROM Department ORDER BY deptName")
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
                """INSERT INTO Staff (personID, employeeID, hireDate, salary)
                   VALUES (%s, %s, %s, %s)""",
                (
                    pid,
                    request.form['employeeID'].strip(),
                    request.form['hireDate'],
                    request.form['salary'],
                )
            )
            execute_update(
                """INSERT INTO Doctor (personID, licenseNumber, specialization,
                       yearsExperience, deptID)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    pid,
                    request.form['licenseNumber'].strip(),
                    request.form['specialization'].strip() or None,
                    request.form['yearsExperience'] or None,
                    request.form['deptID'],
                )
            )
            flash('Doctor created successfully.', 'success')
            return redirect(url_for('doctors.view_doctor', did=pid))
        except Exception as e:
            flash(f'Error creating doctor: {e}', 'danger')
    return render_template('doctors/form.html', doctor=None, departments=departments, action='Create')


@doctors_bp.route('/doctors/<int:did>/edit', methods=['GET', 'POST'])
def edit_doctor(did):
    doctor = execute_query(_DETAIL_SQL, (did,), one=True)
    if not doctor:
        flash('Doctor not found.', 'danger')
        return redirect(url_for('doctors.list_doctors'))
    departments = execute_query("SELECT deptID, deptName FROM Department ORDER BY deptName")
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
                    did,
                )
            )
            execute_update(
                "UPDATE Staff SET salary=%s WHERE personID=%s",
                (request.form['salary'], did)
            )
            execute_update(
                """UPDATE Doctor SET specialization=%s, yearsExperience=%s, deptID=%s
                   WHERE personID=%s""",
                (
                    request.form['specialization'].strip() or None,
                    request.form['yearsExperience'] or None,
                    request.form['deptID'],
                    did,
                )
            )
            flash('Doctor updated successfully.', 'success')
            return redirect(url_for('doctors.view_doctor', did=did))
        except Exception as e:
            flash(f'Error updating doctor: {e}', 'danger')
    return render_template('doctors/form.html', doctor=doctor, departments=departments, action='Edit')


@doctors_bp.route('/doctors/<int:did>/delete', methods=['POST'])
def delete_doctor(did):
    try:
        execute_update("DELETE FROM Person WHERE personID = %s", (did,))
        flash('Doctor deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting doctor: {e}', 'danger')
    return redirect(url_for('doctors.list_doctors'))
