frappe.ui.form.on('Sales Partner', {
	// generate_code: function(frm) {
    //     frm.events.code_generator(frm);
    // },

    custom_generate_code: function(frm) {
        frappe.call({
            method: 'nextproject.nextproject.custom_sales_partner.code_generator',
			// doc:frm.doc,
            callback: function(r) {
                if (r.message) {
                    frm.set_value('referral_code', r.message);
                    frappe.msgprint('New referral code generated: ' + r.message);
                } else {
                    frappe.msgprint('Failed to generate referral code.');
                }
            }
        });
    }
});