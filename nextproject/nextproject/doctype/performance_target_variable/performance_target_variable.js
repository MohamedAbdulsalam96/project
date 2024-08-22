// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Target Variable', {
	// refresh: function(frm) {

	// }

	onload: function (frm) {
		frm.set_query('fiscal_year', function(doc) {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});
	}
});
