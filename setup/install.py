import frappe

def after_install():
    create_default_settings()
    create_default_equipment_categories()
    frappe.db.commit()
    frappe.msgprint("Successfully ")


def create_default_settings():
	settings = frappe.get_single("RentFlow Settings")
	settings.shop_name = settings.shop_name or "RentFlow Equipment Yard"
	settings.manager_email = settings.manager_email or "suresh@gmail.com"
	settings.default_deposit_percent = settings.default_deposit_percent or 20
	settings.damage_fee_per_grade_drop = settings.damage_fee_per_grade_drop or 500
	settings.late_fee_per_day = settings.late_fee_per_day or 100
	settings.low_availability_alert_enabled = 1
	settings.save(ignore_permissions=True)

	                       
def create_default_equipment_categories():
    categories = [
        {
            "category_name": "Power Drill",
            "description": "Electric power drill for construction and maintenance work.",
            "daily_rate": 500,
            "deposit_amount": 2000
        },
        {
            "category_name": "Generator",
            "description": "Portable generator for temporary power supply.",
            "daily_rate": 1500,
            "deposit_amount": 5000
        },
        {
            "category_name": "Scaffold Tower Set",
            "description": "Scaffold tower set for  construction .",
            "daily_rate": 1000,
            "deposit_amount": 4000
        }
    ]

    for category in categories:
        if not frappe.db.exists(
            "Equipment Category",
            category["category_name"]
        ):
            doc = frappe.get_doc({
                "doctype": "Equipment Category",
                "category_name": category["category_name"],
                "description": category["description"],
                "daily_rate": category["daily_rate"],
                "deposit_amount": category["deposit_amount"]
            })

            doc.insert(ignore_permissions=True)

			