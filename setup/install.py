import Frappe
def after_install():
    create_default_settings()
    frappe.db.commit()
    frappe.msgprint("Successfully ")


def create_default_settings():
	settings = frappe.get_doc("RentFlow Settings")
	settings.shop_name = settings.shop_name or "RentFlow Equipment Yard"
	settings.manager_email = settings.manager_email or "suresh@gmail.com"
	settings.default_deposit_percent = settings.default_deposit_percent or 20
	settings.damage_fee_per_grade_drop = settings.damage_fee_per_grade_drop or 500
	settings.late_fee_per_day = settings.late_fee_per_day or 100
	settings.low_availability_alert_enabled = 1
	settings.save(ignore_permissions=True)
