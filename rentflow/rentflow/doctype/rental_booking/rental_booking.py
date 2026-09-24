# Copyright (c) 2026, Sruthika and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.utils import date_diff, flt , today 
from frappe.model.docstatus import DocStatus


GRADE_RANK = {"New": 0, "Good": 1, "Fair": 2, "Poor": 3, "Damaged": 4}

class RentalBooking(Document):
	def validate(self):
		self.validate_dates()
		self.check_overlap()
		self.calculate_totals()
		self.calculate_damage()

	def validate_dates(self):
		if self.start_date and self.end_date and self.start_date > self.end_date:
			frappe.throw("Start date must be  before end date")

	def check_overlap(self):
		RB = DocType("Rental Booking")
		BI = DocType("Booking Item")

		for item in self.items:
		
			conflicts = (
				frappe.qb.from_(RB).join(BI).on(BI.parent == RB.name).select(RB.name).where( (BI.equipment_unit == item.equipment_unit) & (RB.name != (self.name or ""))
					& (RB.docstatus == 1) & (RB.status.notin(("Cancelled", "Returned"))) & (RB.start_date <= self.end_date)
					& (RB.end_date >= self.start_date)
				).run(as_dict=True)
			)
			if conflicts:
				frappe.throw("Equipment unit is already booked for an overlapping period")
				

	def calculate_totals(self):
		rental_total = 0
		for item in self.items:
			if not (item.equipment_unit and self.start_date and self.end_date):
				continue
			days = date_diff(self.end_date, self.start_date) + 1
			item.line_days = days
			item.line_amount = item.daily_rate * days
			rental_total += item.line_amount
		self.rental_total = rental_total

	def calculate_damage(self):

		settings = frappe.get_doc("RentFlow Settings")
		per_grade = flt(settings.damage_fee_per_grade_drop)

		damage_total = 0
		for item in self.items:
			doc = frappe.get_doc("Equipment Unit" , item.equipment_unit)
			g1 = doc.condition_grade
			drop = GRADE_RANK.get(item.checkout_condition_grade) - GRADE_RANK.get(g1) 


			doc2 = frappe.get_doc('RentFlow Settings')
			item.damage_fee =per_grade * drop 
			damage_total += flt(item.damage_fee)

		self.damage_total = damage_total
		self.final_amount = flt(self.rental_total) + flt(self.damage_total)

	
	def before_submit(self):
		if self.status != "Confirmed":
			frappe.throw("Booking must be Confirmed before it can be submitted")
		if  self.deposit_collected < 0:
			frappe.throw("A deposit must be collected before submitting!!")
		self.check_overlap()

	
	def on_submit(self):
		self.status = "Reserved"
		for item in self.items:
			frappe.db.set_value("Equipment Unit", item.equipment_unit, "current_status", "Reserved" )
		self.create_invoice()
		frappe.enqueue(
			"rentflow.rentflow.doctype.rental_booking.rental_booking.send_confirmation_email",
			queue="short",
			booking_name=self.name,
		)
	
	def send_confirmation_email(booking_name):
		doc = frappe.get_doc("Rental Booking", booking_name)
		if not doc.customer_email:
			return
		frappe.sendmail(
			recipients=[doc.customer_email],
			subject=f"Booking Confirmed - {doc.name}",
			message=f"Your rental booking {doc.name} is confirmed for {doc.start_date} to {doc.end_date}. Total: {doc.final_amount}",
		)

	def create_invoice(self):
		invoice = frappe.new_doc("Rental Invoice")
		invoice.rental_booking = self.name
		invoice.rental_amount = self.rental_total
		invoice_date = today
		invoice.damage_amount = self.damage_total
		invoice.total_amount = self.final_amount
		invoice.payment_status = "Unpaid"
		invoice.insert(ignore_permissions=True)

	
	def on_cancel(self):
		self.status = "Cancelled"
		for item in self.items:
			frappe.db.set_value(
				"Equipment Unit", item.equipment_unit, "current_status", "Available", update_modified=False
			) 
		for inv_name in frappe.get_all(
			"Rental Invoice", filters={"rental_booking": self.name, "status": "Unpaid"}, pluck="name"
		):
			inv = frappe.get_doc("Rental Invoice", inv_name)
			inv.status = "Cancelled"
			inv.save(ignore_permissions=True)

	
	def on_trash(self):
		if self.status not in ("Cancelled", "Draft"):
			frappe.throw(_("Only Draft or Cancelled bookings can be deleted"))



# ------------------------------------------------------------------
# E2 - rename integrity: Rental Invoice is autonamed "INV-{rental_booking}",
# so renaming a booking leaves a stale invoice name unless we follow up.
# Frappe's own frappe.rename_doc() already rewrites every Link/Dynamic Link
# field pointing at the renamed doc across the whole system (including
# Rental Invoice.rental_booking) automatically - this hook only handles the
# one thing that's NOT automatic: the invoice's own *name*, which was
# derived from the old booking name at creation time and won't update
# itself just because the field it was built from changed.
# ------------------------------------------------------------------

def on_rental_booking_rename(doc, method=None, old_name=None, new_name=None, merge=False):

	new_name = new_name or doc.name
	invoice_name = frappe.db.get_value("Rental Invoice", {"rental_booking": new_name}, "name")
	if invoice_name and invoice_name != f"INV-{new_name}":
		frappe.rename_doc("Rental Invoice", invoice_name, f"INV-{new_name}", force=True)


# ------------------------------------------------------------------
# D2 - row-level filtering via permission_query_conditions.
#
# get_list (used by the desk UI, reports, and frappe.get_list in server
# code) always runs this condition, so an Inspector's list view and any
# report built on it are automatically scoped. get_all explicitly skips
# permission checks (including this hook) for performance - it is meant for
# trusted, internal, already-permission-checked contexts. Calling get_all
# with user input in the filters, or exposing its result to an under-
# privileged user, is the classic way this kind of row-level restriction
# gets silently bypassed - see N1 for the audit of every place this
# distinction matters in this app.
# ------------------------------------------------------------------
def get_permission_query_conditions(user=None):
	user = user or frappe.session.user
	roles = frappe.get_roles(user)

	if "System Manager" in roles or "Front Desk" in roles:
		return ""

	if "Inspector" in roles:
		staff = frappe.db.get_value("Yard Staff", {"user": user}, "name")
		if not staff:
			return "1=0"
		return f"`tabRental Booking`.handled_by = {frappe.db.escape(staff)}"

	return "1=0"


