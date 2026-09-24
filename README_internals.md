### The snippet below has two bugs related to document lifecycle. Identify both and write the corrected version in README_internals.md:


## Bug 1:
<!-- self.save() -->
** `validate()` is itself called by `save()` as part of the save pipeline. Calling`self.save()` from inside it re-enters the same save pipeline, which calls`validate()` again, which calls `save()` again - unbounded recursion until Python's recursion limit is hit.

## Bug 2 - 
mutating and saving a different document from inside `validate()`. `validate()` can run multiple times before a document isactually persisted That makes the Equipment Unit's status change if the Rental Booking own save later fails for an unrelated reason, the unit is
left "Rented" even though the booking was never actually saved. Side
effects on other documents belong in a lifecycle hook that only runs once


## why would two staff members confirming the same booking at once trigger a "Document has been modified after you have opened it" error, and how does Frappe prevent the silent overwrite?

 When someone enters the form view of a doctype their timestamp modified will be updated so when other person updates the changed the record due to the difference between latest modified and modified the error Document has been modified after you have opened it comes


 
 D2 - row-level filtering via permission_query_conditions.

 get_list always runs this condition, so an Inspector's list view and any report built on it are automatically filtered . get_all explicitly skips
 permission checks  - it is meant for already-permission-checked contexts. 
