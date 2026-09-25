// Copyright (c) 2026, Sruthika and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Rental Booking", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Rental Booking", {

    setup(frm) {

        frm.set_query("equipment_unit", "items", function(doc, cdt, cdn) {

            const row = locals[cdt][cdn];

            const selected_units = (doc.items || [])
                .filter(item => item.name !== row.name)
                .map(item => item.equipment_unit)
                .filter(Boolean);


            return {
                filters: {
                    current_status: "Available",
                    name: ["not in", selected_units]
                }
            };
        });

    }

});

frappe.ui.form.on("Rental Booking", {

    refresh(frm) {

        if (!frm.doc.status) {
            return;
        }

        const status = frm.doc.status;

        const colors = {
            "Draft": "orange",
            "Reserved": "blue",
            "Checked Out": "green",
            "Returned": "gray",
            "Cancelled": "red"
        };

        const color = colors[status] || "gray";

        frm.dashboard.add_indicator(
            status,
            color
        );
    } ,

        refresh(frm) {
        
             let is_allowed = frappe.user_roles.includes('RF Manager');
                frm.toggle_enable(['customer_phone'], is_allowed);
    }
});

frappe.ui.form.on("Rental Booking", {

    refresh(frm) {

        if (frm.doc.status === "Checked Out") {

            frm.add_custom_button(
                "Log Return",
                function() {

                    frappe.msgprint(
                        "Return process started."
                    );

                }
            );
        }
    }
});

frappe.ui.form.on("Rental Booking", {

    start_date(frm) {
        check_rental_duration(frm);
    },

    end_date(frm) {
        check_rental_duration(frm);
    }

});


function check_rental_duration(frm) {

    if (!frm.doc.start_date || !frm.doc.end_date) {
        return;
    }

    const start = frappe.datetime.str_to_obj(
        frm.doc.start_date
    );

    const end = frappe.datetime.str_to_obj(
        frm.doc.end_date
    );

    const difference =
        frappe.datetime.get_day_diff(
            frm.doc.end_date,
            frm.doc.start_date
        );

    if (difference > 30) {

        frappe.msgprint({
            title: "Long Rental Period",
            message:
                "This rental period is longer than 30 days.",
            indicator: "orange"
        });
    }
}

frappe.ui.form.on("Booking Item", {

    quantity(frm, cdt, cdn) {
        calculate_line_amount(frm, cdt, cdn);
    },

    equipment_unit(frm, cdt, cdn) {
        calculate_line_amount(frm, cdt, cdn);
    }
});

function calculate_line_amount(frm, cdt, cdn) {

    const row = locals[cdt][cdn];

    if (
        !row.daily_rate ||
        !frm.doc.start_date ||
        !frm.doc.end_date
    ) {
        frappe.model.set_value(
            cdt,
            cdn,
            "line_amount",
            0
        );

        return;
    }

    const days = frappe.datetime.get_day_diff(frm.doc.end_date,frm.doc.start_date ) + 1;

    const amount =  row.daily_rate * days;

    frappe.model.set_value( cdt, cdn, "line_amount", amount );
}

frappe.ui.form.on("Rental Booking" , {
    refresh(frm) {
    frm.add_custom_button('Log Return', () => {

    let d = new frappe.ui.Dialog({
        title: 'Condition Grade',

        fields: [
            {
                label: 'Select Item',
                fieldname: 'select_item',
                fieldtype: 'Link',
                options: 'Equipment Unit'
            },
            {
                label: 'Condition Grade',
                fieldname: 'condition_grade',
                fieldtype: 'Select',
                options: 'New\nGood\nFair\nPoor\nDamaged'
            },
            {
                label: 'Notes',
                fieldname: 'notes',
                fieldtype: 'Data' , 
                reqd : 1
            }
        ],

        size: 'small',

        primary_action_label: 'Submit',

        primary_action(values) {
            console.log(values);
            d.hide();
        }
    });

    d.show();
});
}
})


frappe.ui.form.on('Rental Booking' , {
    refresh(frm) {
        frm.add_custom_button('Transfer Handler', () => {
            frappe.prompt({
                         label: 'Select Item you wanted to tranfer',
                        fieldname: 'select_item',
                        fieldtype: 'Link',
                        options: 'Equipment Unit'
                }, (values) => {
                                frappe.confirm('Are you sure you want to tranfer this item?',
                  () => {
                                    frappe.call({
				                            method: "rentflow.rentflow.api.book_equip",
                                                    
				callback: () => frm.reload_doc(),
			});
                 }, () => {
                                     frappe.msgprint("The Item will not be transfered")
            
             })

                    frm.trigger("start_date")
        })
        })
    }
})
