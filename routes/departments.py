from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

departments_bp = Blueprint('departments', __name__)

_LIST_SQL = """
    SELECT d.deptID, d.deptName, d.location, d.phone,
           COUNT(DISTINCT doc.personID) AS doctorCount,
           COUNT(DISTINCT r.roomID) AS roomCount
    FROM Department d
    LEFT JOIN Doctor doc ON doc.deptID = d.deptID
    LEFT JOIN Room r     ON r.deptID   = d.deptID
    GROUP BY d.deptID, d.deptName, d.location, d.phone
    ORDER BY d.deptName
"""


@departments_bp.route('/departments')
def list_departments():
    departments = execute_query(_LIST_SQL)
    return render_template('departments/list.html', departments=departments)


@departments_bp.route('/departments/new', methods=['GET', 'POST'])
def new_department():
    if request.method == 'POST':
        try:
            execute_update(
                "INSERT INTO Department (deptName, location, phone) VALUES (%s, %s, %s)",
                (
                    request.form['deptName'].strip(),
                    request.form['location'].strip() or None,
                    request.form['phone'].strip() or None,
                )
            )
            flash('Department created.', 'success')
            return redirect(url_for('departments.list_departments'))
        except Exception as e:
            flash(f'Error creating department: {e}', 'danger')
    return render_template('departments/form.html', dept=None, action='Create')


@departments_bp.route('/departments/<int:did>/edit', methods=['GET', 'POST'])
def edit_department(did):
    dept = execute_query(
        "SELECT * FROM Department WHERE deptID = %s", (did,), one=True
    )
    if not dept:
        flash('Department not found.', 'danger')
        return redirect(url_for('departments.list_departments'))
    if request.method == 'POST':
        try:
            execute_update(
                "UPDATE Department SET deptName=%s, location=%s, phone=%s WHERE deptID=%s",
                (
                    request.form['deptName'].strip(),
                    request.form['location'].strip() or None,
                    request.form['phone'].strip() or None,
                    did,
                )
            )
            flash('Department updated.', 'success')
            return redirect(url_for('departments.list_departments'))
        except Exception as e:
            flash(f'Error updating department: {e}', 'danger')
    return render_template('departments/form.html', dept=dept, action='Edit')


@departments_bp.route('/departments/<int:did>/delete', methods=['POST'])
def delete_department(did):
    try:
        execute_update("DELETE FROM Department WHERE deptID = %s", (did,))
        flash('Department deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting department: {e}', 'danger')
    return redirect(url_for('departments.list_departments'))
