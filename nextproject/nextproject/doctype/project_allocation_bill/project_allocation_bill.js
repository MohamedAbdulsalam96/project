// Copyright (c) 2022, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Allocation Bill', {
	setup: function(frm) {
		frm.set_query("project", function() {
			return {
				filters: {
					"billing_based_on": "Allocation Based",
					
				}
			};
		});
		
	},
	refresh:function(frm){
		if(frm.doc.docstatus==0 && !frm.doc.__islocal){
			frm.add_custom_button('Recalculated', function() {
				frm.call({
					method:"recalculate",
					doc:frm.doc,
					
					callback: function(r) {
						if (r.message){
							
						}
						
					}
				});


			})
		}
		
		if(frm.doc.docstatus==1 && frm.doc.state!="Completed"){
			
			frm.call({
				method:"get_project_allo_bill",
				doc:frm.doc,
				
				callback: function(r) {
					if(r.message){
						frm.add_custom_button('Create Sales Invoice/Order', function() {
							frm.call({
								method:"make_sales_invoice",
								doc:frm.doc,
								
								callback: function(r) {
									if (r.message){
										frappe.msgprint("Sales Invoice/Order Created")
									}
									
								}
							});
						});
					}
					
				}
			});

			
		
		}
		if(frm.doc.docstatus==1 && frm.doc.state!="Completed"){
			frm.add_custom_button('Get Reconcilation Items', function() {
				frm.call({
					method:"get_reconciled_allocation",
					doc:frm.doc,
					
					callback: function(r) {
						
						
							$.each(r.message,function(i,row1){
							console.log(row1)
							var childTable = frm.add_child("rec_items");
							childTable.task=row1.task
							childTable.task=row1.task
							childTable.parentfield="reconciliation_items"
							childTable.subject=row1.subject
							childTable.timesheet_hours=row1.timesheet_hours
							childTable.parent=row1.parent
							childTable.parenttype=row1.parenttype
							childTable.allocation_in_hours=row1.allocation_in_hours
							childTable.difference_in_hours=row1.difference_in_hours
							})
							frm.refresh_fields("rec_items");
						frm.save("Update")
						}
				});
			});
		}
	}
});
