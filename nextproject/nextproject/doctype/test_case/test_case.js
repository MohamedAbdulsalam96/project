// Copyright (c) 2021, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Test Case', {
	onload: function(frm) {
		frm.set_query("task", function() {
				return {
					filters: {
						"project": frm.doc.project,
					}
				}
			});			
		}});


