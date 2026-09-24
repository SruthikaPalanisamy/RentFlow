import frappe


IGNORED_DOCTYPES = {"Version","Error Log","Activity Log","Route History","Access Log","Audit Log"}


def log_change(doc, method=None):

	if doc.doctype in IGNORED_DOCTYPES or doc.doctype.startswith("__"):
		return
	try:
		action = (method or "on_update").removeprefix("on_").replace("_", " ").title()
		frappe.get_doc(
			{
				"doctype": "Audit Log",
				"doctype_name": doc.doctype,
				"document_name": doc.name,
				"action": action,
				"user": frappe.session.user,
				"timestamp": frappe.utils.now(),
			}
		).insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "rentflow audit log failed")
