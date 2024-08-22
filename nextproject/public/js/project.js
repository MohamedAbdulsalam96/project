// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
frappe.ui.form.on("Project", {

    refresh: function (frm) {
        
        // frm.doc.billing_based_on.onchange = function (frm) {
            
        // }

        // frm.fields_dict['billing_based_on'].df.onchange = function() {
        //     // Your logic based on the value of billing_based_is
        //     var billingBasedIsValue = frm.doc.billing_based_is;
        //     if (['Timesheet Based', 'Milestone Based', 'Allocation Based'].includes(billingBasedIsValue)) {
        //         // Show or hide fields, perform other actions, etc.
        //         frm.fields_dict['custom_imesheet_overage_allowed_in__'].toggle_display(true);
        //     } else {
        //         frm.fields_dict['custom_imesheet_overage_allowed_in__'].toggle_display(false);
        //     }
        // };


        if(frm.doc.status=="Open"){

        frm.add_custom_button(__('Re-Assign Tasks'), function() {
            frappe.confirm( "This will update all the tasks connected with this project and re-assign them to the current team set on the project. Do you want to continue?",
            () => {
                let d = new frappe.ui.Dialog({
                    title: 'Update Task',
                    fields: [
                        {
                            label: 'Employee Group',
                            fieldname: 'employee_group',
                            fieldtype: 'Link',
                            options: 'Employee Group',
                            ignore_user_permissions: 1,
                            reqd:1                    
                        },
                        {
                            label:'Project Lead',
                            fieldname: 'project_lead',
                            fieldtype: 'Link',
                            options: 'Employee',
                            ignore_user_permissions: 1,
                            reqd:1,
                            default: frm.doc.project_lead        
                        },
                        {
                            label:'Primary Consultant',
                            fieldname: 'primary_consultant',
                            fieldtype: 'Link',
                            options: 'Employee',
                            ignore_user_permissions: 1,
                            reqd:1         
                        },
                        {
                            label:'Department',
                            fieldname: 'department',
                            fieldtype: 'Link',
                            options: 'Department',
                            ignore_user_permissions: 1,
                            reqd:1         
                        },
                        {
                            label:'Company',
                            fieldname: 'company',
                            fieldtype: 'Link',
                            options: 'Company',
                            ignore_user_permissions: 1,
                            reqd:1        
                        }
                    ],
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        console.log(values);
                        frm.call({
                            method:"nextproject.nextproject.project.update_task",
                            args: {
                                values:values,
                                project:frm.doc.name
                            },
                            callback: function(r) {
                                if(r.message){
                                    
                                    }
                                }
                        });
                        d.hide();
                    }
                });
                
                d.show();
            }, () => {
                // action to perform if No is selected
            })
        



        })
    }
    },
    
    onload: function (frm) {
        frm.trigger("billing_based_on")
        frm.set_query("billing_item", function() {
			return {
				"filters": {
					is_sales_item: 1,
				}
			}
		});
        frm.set_query("terms", function() {
			return {
				"filters": {
					selling: 1,
				}
			}
		});
        frm.call({
            method:"nextproject.nextproject.project.sales_order_naming_series",
            args: {
            },
            callback: function(r) {
                if(r.message){
                    frm.set_df_property("sales_order_naming_series", "options",r.message);
                    }
                }
        });
        frm.call({
            method:"nextproject.nextproject.project.sales_invoice_naming_series",
            args: {
            },
            callback: function(r) {
                if(r.message){
                    frm.set_df_property("sales_invoice_naming_series", "options",r.message);
                    }
                }
        });
        if(! frm.doc.__islocal){

             frm.fields_dict['milestone'].grid.get_field("milestone").get_query =
                    function(doc, cdt, cdn) {
                      var child = locals[cdt][cdn];
                        return {
                         filters: [
                         ['Task','project','=',frm.doc.name]
                     ]
                  }
              }

          }
            frm.add_custom_button(__('Expense Invoice'), () => {
            let d = new frappe.ui.Dialog({
                "title": __("Expense Invoice"),
                "fields": [
                    {
                        "fieldname": "from_date",
                        "fieldtype": "Date",
                        "label": "From Date",
                        "reqd": 1,
                    },
                    {
                        "fieldname": "to_date",
                        "fieldtype": "Date",
                        "label": "To Date",
                        "reqd": 1,
                    },
                    {
                        "fieldname": "project",
                        "fieldtype": "Link",
                        "label": "Project",
                        "read_only": 1,
                        "default":frm.doc.name
                    },
                ],
                primary_action_label: 'Submit',
                primary_action(values,name) {
                    console.log(values,name);
                    frm.call({
                        method:"nextproject.nextproject.project.get_expense_claim",
                        args: {
                            values:values,
                            name:frm.doc.name
                        },
                        callback: function(r) {
                            if(r.message){
                                
                                }
                            }
                    });
                    d.hide();
                },
                // primary_action_label: 'Submit',
                // primary_action: function() {
                //     frm.events.set_status(frm, d.get_values().status);
                //     d.hide();
                // },
                primary_action_label: __("Expense Invoice")
            }).show();
        }, __("Actions"))


	},
    billing_based_on:function(frm){
        if(frm.doc.billing_based_on == 'Allocation Based'){
            frm.set_df_property("billing_frequency", "options",["Weekly","Monthly","Bi-Monthly"])
        }
        if(frm.doc.billing_based_on != 'Allocation Based'){
            frm.set_df_property("billing_frequency", "options",["Daily","Weekly","Monthly","Quaterly","Bi-Yearly","Yearly","Custom"])
        
        }
    },
	validate: function(frm){
	    var total = 0;
        $.each(frm.doc["milestone"],function(i, milestone)
            {
                 total = total += milestone.billing_percentage;
            });
        if (total > 100){
            frappe.throw("Total Billing Percentage Not Greater Than 100");
        }
	},

	after_save: function(frm){
        frm.call({
            method:"nextproject.task.daily_project",
            args: {
                project:frm.doc.name
            },
            callback: function(r) {
                if(r.message){
                        console.log("***",r.message);
                    }
                }
        });
        frm.call({
            method:"nextproject.task.cr_method",
            args: {
                project:frm.doc.name
            },
            callback: function(r) {
                if(r.message){
                        console.log("***",r.message);
                    }
                }
        });
	},

	auto_submit_order: function(frm){
	    frm.doc.auto_submit_invoice = 0;
	},

	auto_submit_invoice: function(frm){
	    frm.doc.auto_submit_order =0;

	},

    billing_charges_based_on_project_timesheet_charges: function(frm){
        frm.doc.billing_charges_based_on_activity_cost = 0;
        frm.refresh_field("billing_charges_based_on_activity_cost");
    },

    billing_charges_based_on_activity_cost: function(frm){
        frm.doc.billing_charges_based_on_project_timesheet_charges = 0;
        frm.refresh_field("billing_charges_based_on_project_timesheet_charges");
    },

	auto_creation_doctype: function(frm){
	    if(frm.doc.auto_creation_doctype == "Sales Invoice"){
	        frm.doc.auto_submit_order =0;
	    }
	    if(frm.doc.auto_creation_doctype == "Sales Order"){
	        frm.doc.auto_submit_invoice = 0;
	    }
	}


});
