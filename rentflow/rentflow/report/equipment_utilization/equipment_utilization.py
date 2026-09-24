import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{"label": _("Category"), "fieldname": "category", "fieldtype": "Link", "options": "Equipment Category", "width": 160},
		{"label": _("Total Units"), "fieldname": "total_units", "fieldtype": "Int", "width": 10},
		{"label": _("Currently Rented"), "fieldname": "rented", "fieldtype": "Int", "width": 130},
		{"label": _("Utilization %"), "fieldname": "utilization_pct", "fieldtype": "Percent", "width": 120},
		{"label": _("Bookings"), "fieldname": "booking_count", "fieldtype": "Int", "width": 100},
	]


def get_data(filters):
	
	categories = frappe.get_list(
		"Equipment Category", fields=["name as category"], order_by="category_name asc"
	)

	EU = DocType("Equipment Unit")
	BI = DocType("Booking Item")
	RB = DocType("Rental Booking")

	rows = []
	for cat in categories:
		total_units = frappe.db.count("Equipment Unit", {"category": cat.category, "is_active": 1})
		rented = frappe.db.count(
			"Equipment Unit", {"category": cat.category, "is_active": 1, "current_status": "Rented"}
		)
		booking_count = (
			frappe.qb.from_(BI)
			.join(EU)
			.on(EU.name == BI.equipment_unit)
			.join(RB)
			.on(RB.name == BI.parent)
			.select(Count(RB.name).distinct())
			.where((EU.category == cat.category) & (RB.docstatus == 1))
			.run()[0][0]
		)
		rows.append(
			{
				"category": cat.category,
				"total_units": total_units,
				"rented": rented,
				"utilization_pct": round((rented / total_units) * 100, 1) if total_units else 0,
				"booking_count": booking_count or 0,
			}
		)
	return rows


def get_chart(data):
	return {
		"data": {
			"labels": [d["category"] for d in data],
			"datasets": [{"name": _("Utilization %"), "values": [d["utilization_pct"] for d in data]}],
		},
		"type": "bar",
	}


def get_report_summary(data):
	if not data:
		return []
	avg_util = round(sum(d["utilization_pct"] for d in data) / len(data), 1)
	return [
		{"label": _("Categories"), "value": len(data), "datatype": "Int"},
		{"label": _("Avg Utilization"), "value": avg_util, "datatype": "Percent"},
	]
