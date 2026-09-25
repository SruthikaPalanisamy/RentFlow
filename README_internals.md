
# B3 -  Dangerous Patterns


### The snippet below has two bugs related to document lifecycle. Identify both and write the corrected version in README_internals.md:


## Bug 1:
<!-- self.save() -->
** `validate()` is itself called by `save()` as part of the save pipeline. Calling`self.save()` from inside it re-enters the same save pipeline, which calls`validate()` again, which calls `save()` again - unbounded recursion until Python's recursion limit is hit.

## Bug 2 -  unit.save()
mutating and saving a different document from inside `validate()`. `validate()` can run multiple times before a document isactually persisted That makes the Equipment Unit's status change if the Rental Booking own save later fails for an unrelated reason, the unit is
left "Rented" even though the booking was never actually saved. Side
effects on other documents belong in a lifecycle hook that only runs once

# The corrected Code:

def validate(self):
    self.rental_total = sum(r.line_amount for r in self.items)
    # no self.save(), no touching other documents here

def on_submit(self):
    for item in self.items:
        frappe.db.set_value(
            "Equipment Unit", item.equipment_unit, "current_status", "Reserved",
            update_modified=False,
        )


## why would two staff members confirming the same booking at once trigger a "Document has been modified after you have opened it" error, and how does Frappe prevent the silent overwrite?

 When someone enters the form view of a doctype their timestamp modified will be updated so when other person updates the changed the record due to the difference between latest modified and modified the error Document has been modified after you have opened it comes


 
 ## D2 - row-level filtering via permission_query_conditions.

 get_list always runs this condition, so an Inspector's list view and any report built on it are automatically filtered . get_all explicitly skips
 permission checks  - it is meant for already-permission-checked contexts. 



## E1 - the `on_update()` recursion pitfall

```python
def on_update(self):
    self.save()  # recomputes final_amount, supposedly
```

`on_update()` is itself called *by* the save pipeline (after `validate()` and the DB write, on every successful save,
draft or submit). Calling `self.save()` from inside `on_update()` re-triggers the entire save pipeline - `validate()` runs again, which
succeeds, which calls `on_update()` again, which calls `save()` again -
infinite recursion until `RecursionError`.

The fix is to recognize that `on_update()` had no work to do : `validate()` already recomputes `rental_total`,`damage_total`, and `final_amount` on every single save (draft or submit), because `validate()` runs unconditionally as part of that same save. There
is nothing left for `on_update()` to "recompute" - it runs *after* the
values are already written. `rental_booking.py`'s `on_update()` is
deliberately empty for this reason.

# E2  Explain when merge=True would be dangerous.
When you give merge= True the doctypes containing the same document name will the merged as a single document which will result in collapse of 2 documents

# E3 One Performance Judgment Call

`api.get_booking_status()` uses `frappe.db.get_value
with an explicit field list instead of `frappe.get_doc()`. `get_doc()`
fetches  a full Document object - loads every field, runs `__init__`
, attaches child tables. For a read-only status check with 5 fields `get_doc()` would be meaningfully more so its better to use get_value

# H1
# why does a frappe.call inside the validate client event not work, and why must async availability checks happen in onload/refresh instead?

Because frappe.call is asynchronous so if you call frappe.call inside validate , the frappe needs to save the document and continue its pipeline and perform its synchronous activity 



## k2
# N+1 PROBLEM - fix this
# bookings = frappe.get_all("Rental Booking", fields=["name","handled_by"])
# for b in bookings:
#    staff = frappe.get_doc("Yard Staff", b.handled_by)
#    print(staff.staff_name, staff.phone)

bookings = frappe.get_all(
    "Rental Booking",
    fields=["name", "handled_by"]
)

staff_names = [b.handled_by for b in bookings if b.handled_by]

staff_records = frappe.get_all(
    "Yard Staff",
    filters={"name": ["in", staff_names]},
    fields=["name", "staff_name", "phone"]
)

staff_map = {
    staff.name: staff
    for staff in staff_records
}

for b in bookings:
    staff = staff_map.get(b.handled_by)

    if staff:
        print(staff.staff_name, staff.phone)


## Test the standard /api/resource/Rental Booking CRUD once with curl and document one request/response pair. 

# GET Request
curl -X GET "http://localhost:8000/api/resource/Rental%20Booking/RB-2026-00004" \
  -H "Authorization: token 8a3494cabe17926:c017b67cc61d14d"

{"data":{"name":"RB-2026-00004","owner":"Administrator","creation":"2026-09-23 14:25:39.299542","modified":"2026-09-23 14:25:39.299542","modified_by":"Administrator","docstatus":0,"idx":0,"customer_name":"Sruthika Palanisamy","customer_phone":"09500890481","start_date":"2026-09-01","end_date":"2026-09-23","deposit_collected":0.0,"rental_total":11500.0,"damage_total":0.0,"final_amount":0.0,"payment_status":"","status":"","doctype":"Rental Booking","items":[{"name":"i3h0iu8akd","owner":"Administrator","creation":"2026-09-23 14:25:39.299542","modified":"2026-09-23 14:25:39.299542","modified_by":"Administrator","docstatus":0,"idx":1,"equipment_unit":"GEN-00001","category":"Generator","daily_rate":"500","line_days":23,"line_amount":11500.0,"parent":"RB-2026-00004","parentfield":"items","parenttype":"Rental Booking","doctype":"Booking Item"}]}}

# POST Request
curl -X POST "http://localhost:8000/api/resource/Rental%20Booking" -H "Authorization: token 8a3494cabe17926:c017b67cc61d14d" -H "Content-Type: application/json" -d '{
    "customer_name": "John Doe",
    "start_date": "2026-09-25",
    "end_date": "2026-09-30",
    "status": "Checked Out" ,"customer_phone": "9588892362" }'
{"data":{"name":"RB-2026-00014","owner":"Administrator","creation":"2026-09-25 14:14:02.438736","modified":"2026-09-25 14:14:02.438736","modified_by":"Administrator","docstatus":0,"idx":0,"customer_name":"John Doe","customer_phone":"9588892362","start_date":"2026-09-25","end_date":"2026-09-30","deposit_collected":0.0,"rental_total":0.0,"damage_total":0.0,"final_amount":0.0,"payment_status":"","status":"Checked Out","doctype":"Rental Booking","items":[] }}

# PUT Request
curl -X PUT "http://localhost:8000/api/resource/Rental%20Booking/RB-2026-00013" -H "Authorization:token 8a3494cabe17926:c017b67cc61d14d" -H "Content-Type: application/json" -d 'application/json" -d '{
    "status": "Checked Out"
}'

{"data":{"name":"RB-2026-00013","owner":"Administrator","creation":"2026-09-24 12:18:09.636539","modified":"2026-09-25 14:17:40.655088","modified_by":"Administrator","docstatus":0,"idx":0,"customer_name":"Sruthika Palanisamy","customer_phone":"09500890481","start_date":"2026-09-25","end_date":"2026-09-26","deposit_collected":0.0,"rental_total":3000.0,"damage_total":500.0,"final_amount":3500.0,"payment_status":"","status":"Checked Out","doctype":"Rental Booking","items":[{"name":"j50ioj4m8g","owner":"Administrator","creation":"2026-09-24 12:18:09.636539","modified":"2026-09-25 14:17:40.655088","modified_by":"Administrator","docstatus":0,"idx":1,"equipment_unit":"SCA-00001","category":"Scaffold Tower","daily_rate":1500.0,"line_days":2,"line_amount":3000.0,"checkout_condition_grade":"Fair","parent":"RB-2026-00013","parentfield":"items","parenttype":"Rental Booking","doctype":"Booking Item"}]}}

# Delete Request
 curl -X DELETE "http://localhost:8000/api/resource/Rental%20Booking/RB-2026-00015" -H "Authorization: 8a3494
cabe17926:c017b67cc61d14d"
{"data":"ok"}

# N1 — ignore_permissions Audit & JS-Hiding Pitfall

# List every use of ignore_permissions=True; justify each in one sentence. Add a JS field hide on customer_phone for non-managers, then show a direct API call can still retrieve it. Explain why hiding a field in JavaScript is not a security measure.

ignore_permissions= Trues bypasses all the permissions for the opened doctypes and lets you to access it
Hiding in js feild is not a security measure becuase using depends_on function only hides what is rendered in the browser Attackers can easily see it using REST API or using frappe.call() 

let is_allowed = frappe.user_roles.includes('RF Manager');
frm.toggle_enable(['customer_phone'], is_allowed);

Even with this conditions people can still view the customer_phone using REST api calls so it is advised not to use js for permisions so use permission conditions query