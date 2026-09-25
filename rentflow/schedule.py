import frappe
from frappe.utils import today


def flag_overdue_returns():

    last_run = frappe.db.get_value(
        "Audit Log",
        {
            "action": "overdue_check",
            "date": today()
        },
        "name"
    )

    if last_run:
        return  

    from rentflow.rentflow.api import get_overdue_returns

    overdue = get_overdue_returns()

    if not overdue:
        return

    settings = frappe.get_single("RentFlow Settings")

    frappe.sendmail(
        recipients=[settings.manager_email],
        subject=f"RentFlow: {len(overdue)} overdue return(s)",
        message=frappe.render_template(
            """
            <ul>
                {% for row in overdue %}
                    <li>
                        {{ row.name }} -
                        {{ row.customer_name }}
                        (due {{ row.end_date }})
                    </li>
                {% endfor %}
            </ul>
            """,
            {"overdue": overdue}
        )
    )

    audit_log = frappe.get_doc({
        "doctype": "Audit Log",
        "action": "overdue_check",
        "date": today()
    })

    audit_log.insert(ignore_permissions=True)

    frappe.db.commit()
        