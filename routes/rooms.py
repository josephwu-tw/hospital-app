from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

rooms_bp = Blueprint('rooms', __name__)

_LIST_SQL = """
    SELECT r.roomID, r.roomNumber, r.roomType, r.floor, r.capacity,
           r.status, d.deptName, d.deptID
    FROM Room r
    JOIN Department d ON r.deptID = d.deptID
    ORDER BY r.roomNumber
"""


@rooms_bp.route('/rooms')
def list_rooms():
    rooms = execute_query(_LIST_SQL)
    departments = execute_query("SELECT deptID, deptName FROM Department ORDER BY deptName")
    return render_template('rooms/list.html', rooms=rooms, departments=departments)


@rooms_bp.route('/rooms/new', methods=['GET', 'POST'])
def new_room():
    departments = execute_query("SELECT deptID, deptName FROM Department ORDER BY deptName")
    if request.method == 'POST':
        try:
            execute_update(
                """INSERT INTO Room (roomNumber, roomType, floor, capacity, status, deptID)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    request.form['roomNumber'].strip(),
                    request.form['roomType'],
                    request.form['floor'].strip() or None,
                    request.form['capacity'] or None,
                    request.form['status'],
                    request.form['deptID'],
                )
            )
            flash('Room created.', 'success')
            return redirect(url_for('rooms.list_rooms'))
        except Exception as e:
            flash(f'Error creating room: {e}', 'danger')
    return render_template('rooms/form.html', room=None, departments=departments, action='Create')


@rooms_bp.route('/rooms/<int:rid>/edit', methods=['GET', 'POST'])
def edit_room(rid):
    room = execute_query(
        "SELECT r.*, d.deptName FROM Room r JOIN Department d ON r.deptID=d.deptID WHERE r.roomID=%s",
        (rid,), one=True
    )
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('rooms.list_rooms'))
    departments = execute_query("SELECT deptID, deptName FROM Department ORDER BY deptName")
    if request.method == 'POST':
        try:
            execute_update(
                """UPDATE Room SET roomNumber=%s, roomType=%s, floor=%s,
                       capacity=%s, status=%s, deptID=%s
                   WHERE roomID=%s""",
                (
                    request.form['roomNumber'].strip(),
                    request.form['roomType'],
                    request.form['floor'].strip() or None,
                    request.form['capacity'] or None,
                    request.form['status'],
                    request.form['deptID'],
                    rid,
                )
            )
            flash('Room updated.', 'success')
            return redirect(url_for('rooms.list_rooms'))
        except Exception as e:
            flash(f'Error updating room: {e}', 'danger')
    return render_template('rooms/form.html', room=room, departments=departments, action='Edit')


@rooms_bp.route('/rooms/<int:rid>/delete', methods=['POST'])
def delete_room(rid):
    try:
        execute_update("DELETE FROM Room WHERE roomID = %s", (rid,))
        flash('Room deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting room: {e}', 'danger')
    return redirect(url_for('rooms.list_rooms'))
