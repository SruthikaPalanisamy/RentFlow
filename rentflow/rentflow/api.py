import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.utils import today


@frappe.whitelist()
def get_overdue_returns():
	RB = DocType("Rental Booking")
	result = (
		frappe.qb.from_(RB)
		.select(RB.name, RB.customer_name, RB.end_date)
		.where((RB.status == "Checked Out") & (RB.end_date < today()))
		.orderby(RB.end_date)
		.run(as_dict=True))
	return result


@frappe.whitelist()
def reassign_bookings(from_staff, to_staff):
	try:
		frappe.db.sql(
			"""
			UPDATE `tabRental Booking`
			SET handled_by = %(to_staff)s
			WHERE handled_by = %(from_staff)s
			  AND docstatus = 1
			  AND status NOT IN ('Returned', 'Cancelled')
			""",
			{"from_staff": from_staff, "to_staff": to_staff},
		)
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "reassign_bookings failed")
		raise

	return {"reassigned_from": from_staff, "reassigned_to": to_staff}

@frappe.whitelist()
def book_equip():
	frappe.msgprint("The method has been called")