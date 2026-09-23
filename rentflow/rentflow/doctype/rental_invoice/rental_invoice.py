# Copyright (c) 2026, Sruthika and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe.model.naming import make_autoname

class RentalInvoice(Document):
    def before_save(self):
        self.invoice_date = today()
    def autoname(self):
        self.invoice_number = make_autoname("INV-.YYYY.-.#####")
   