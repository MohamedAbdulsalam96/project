// Copyright (c) 2021, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Milestone Sign Off', {
	refresh: function(frm) {
		frm.call({
			method:"milestone_list",
			doc: frm.doc,
			callback: function(r) {
				if(r.message){
					  refresh_field("milestone_depends_on_task")
					}
				}
		});
		
		frm.fields_dict['milestone_depends_on_task'].grid.get_field('task').get_query= function(doc,cdt,cdn){
			var child=locals[cdt][cdn];
			return{
				filters:[
					['project','=',frm.doc.project]
				]
			}
		}
	}
});

