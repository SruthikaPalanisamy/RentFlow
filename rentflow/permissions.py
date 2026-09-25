import frappe

def perm_query(user=None):
	user = user or frappe.session.user
	roles = frappe.get_roles(user)

	if "System Manager" in roles or "Front Desk" in roles:
		return ""

	if "RF Inspector" in roles:
		staff = frappe.db.get_value("Yard Staff", {"user": user}, "name")
		if not staff:
			return "1=0"
		return f" `tabRental Booking`.`handled_by` = '{staff}'"

	return "1=0"
