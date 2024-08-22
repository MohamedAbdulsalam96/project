// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Risk', {
	// refresh: function(frm) {

	// }

	onload: function (frm) {
		frm.set_query('primary_task_affected', function(doc) {
			return {
				filters: {
					"project": frm.doc.project,
					"status":["!=", "Cancelled"]
				}
			};
		});
	}
});
