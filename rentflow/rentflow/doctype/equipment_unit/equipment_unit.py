# Copyright (c) 2026, Sruthika and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class EquipmentUnit(Document):
	def autoname(self):
		category_name = frappe.db.get_value(
			"Equipment Category",
			self.category,
			"category_name",  
		) or self.category

		prefix = category_name[:3].upper()
		self.name = make_autoname(f"{prefix}-.#####")
