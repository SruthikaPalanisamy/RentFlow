# Copyright (c) 2026, Sruthika and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import today


class RentalInvoice(Document):
		def before_insert(doc, method):
    		if not doc.invoice_date:
        		doc.invoice_date = today()
