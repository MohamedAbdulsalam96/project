frappe.ui.form.on('Appointment', {
    refresh: function (frm) {
        console.log(" appointment with : ", frm.doc.appointment_with)
        console.log(" party : ", frm.doc.party)
        if ((frm.doc.appointment_with == "Lead") || (!frm.doc.appointment_with)) {
            if (!frm.doc.party) {
                frm.add_custom_button(__('Create Lead'), function () {
                    frappe.call({
                        method: "nextproject.nextproject.custom_appointments.create_lead",
                        args: {
                            contact_name: frm.doc.customer_name,
                            contact_number: frm.doc.customer_phone_number,
                            contact_skype: frm.doc.customer_skype,
                            contact_notes: frm.doc.customer_details,
                            contact_email: frm.doc.customer_email,
                            referral_code: frm.doc.custom_referral_code
                        },
                        callback: function (response) {
                            if (response.message) {
                                frappe.show_alert("Lead created successfully.", 5);
                                // frm.doc.party = response.message
                                frm.set_value('party', response.message);
                                frm.save();
                            } else {
                                console.error("Failed to create lead:", response.exc);
                                frappe.msgprint("Failed to create lead. Please try again.");
                            }
                        }
                    });
                })
            }
        }
    }
});