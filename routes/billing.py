from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

billing_bp = Blueprint('billing', __name__)

_LIST_SQL = """
    SELECT b.billingID, b.totalAmount, b.amountPaid, b.paymentStatus,
           b.billingDate, b.dueDate,
           (b.totalAmount - b.amountPaid)            AS outstanding,
           CONCAT(p.firstName, ' ', p.lastName)      AS patientName,
           CONCAT(doc.firstName, ' ', doc.lastName)  AS doctorName,
           a.appointmentID
    FROM Billing b
    JOIN Appointment a ON b.appointmentID = a.appointmentID
    JOIN Person p      ON a.patientID     = p.personID
    JOIN Person doc    ON a.doctorID      = doc.personID
    ORDER BY b.billingDate DESC
"""

_DETAIL_SQL = """
    SELECT b.*,
           (b.totalAmount - b.amountPaid)       AS outstanding,
           CONCAT(p.firstName, ' ', p.lastName) AS patientName,
           ins.providerName, ins.policyNumber
    FROM Billing b
    JOIN Appointment a  ON b.appointmentID = a.appointmentID
    JOIN Person p       ON a.patientID     = p.personID
    LEFT JOIN Insurance ins ON b.insuranceID = ins.insuranceID
    WHERE b.billingID = %s
"""


@billing_bp.route('/billing')
def list_billing():
    records = execute_query(_LIST_SQL)
    total_unpaid = execute_query(
        "SELECT COALESCE(SUM(totalAmount - amountPaid), 0) AS n FROM Billing WHERE paymentStatus != 'Paid'",
        one=True
    )['n']
    return render_template('billing/list.html', records=records, total_unpaid=total_unpaid)


@billing_bp.route('/billing/<int:bid>/edit', methods=['GET', 'POST'])
def edit_billing(bid):
    record = execute_query(_DETAIL_SQL, (bid,), one=True)
    if not record:
        flash('Billing record not found.', 'danger')
        return redirect(url_for('billing.list_billing'))
    if request.method == 'POST':
        try:
            amount_paid = float(request.form['amountPaid'])
            total       = float(request.form['totalAmount'])
            status = 'Paid' if amount_paid >= total else (
                     'Partial' if amount_paid > 0 else 'Unpaid')
            execute_update(
                """UPDATE Billing
                   SET totalAmount=%s, amountPaid=%s, paymentStatus=%s, dueDate=%s
                   WHERE billingID=%s""",
                (total, amount_paid, status, request.form['dueDate'], bid)
            )
            flash('Billing record updated.', 'success')
            return redirect(url_for('billing.list_billing'))
        except Exception as e:
            flash(f'Error updating billing: {e}', 'danger')
    return render_template('billing/form.html', record=record)
