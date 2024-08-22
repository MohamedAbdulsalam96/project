// frappe.ui.form.on("HD Ticket", {
//     refresh:function(frm){
//         frm.add_custom_button(__('Task'), function() {
//             frappe.model.open_mapped_doc({
//                 method: "nextproject.api.make_task",
//                 frm: frm
//             });

//         }, __("Create"));
//         frappe.db.get_value('Sales Invoice', {"ticket":frm.doc.name,"docstatus":["!=",2]}, 'name', (d) => {
//         console.log(d.name)
//         if(!d.name){
//         frm.add_custom_button(__('Sales Invoice'), function() {
//             frappe.model.open_mapped_doc({
//                 method: "nextproject.api.make_invoice",
//                 frm: frm
//             });
//         }, __("Create"));
//         }
//         })
//     }
+

frappe.ui.form.on("HD Ticket", {

    refresh: function (frm) {
        console.log("refresh working");
        frm.add_custom_button('Task', () => {
            console.log("test button");
            let d = new frappe.ui.Dialog({
                title: 'Enter details',
                fields: [
                    {
                        label: 'Subject',
                        fieldname: 'subject',
                        fieldtype: 'Data',
                        default: frm.doc.subject
                    },
                    {
                        label: 'Company',
                        fieldname: 'company',
                        fieldtype: 'Link',
                        options: 'Company',
                        default: frappe.defaults.get_user_default("Company"),
                        ignore_user_permissions: 1
                    },
                    {
                        label: 'Project',
                        fieldname: 'project',
                        fieldtype: 'Link',
                        options: 'Project',
                        ignore_user_permissions: 1,
                        default: frm.doc.custom_project,
                        reqd: 1
                    },
                    {
                        label: 'Expected Start Date',
                        fieldname: 'exp_start_date',
                        fieldtype: 'Date'
                    },
                    {
                        label: 'Expected End Date',
                        fieldname: 'exp_end_date',
                        fieldtype: 'Date'
                    },
                    {
                        label: 'Expected Time',
                        fieldname: 'expected_time',
                        fieldtype: 'Float'
                    },
                    {
                        label: 'Priority',
                        fieldname: 'priority',
                        fieldtype: 'Select',
                        options: ["Low", "Medium", "High", "Urgent"],
                        default:frm.doc.priority
                    },
                    {
                        fieldname: 'column_break',
                        fieldtype: 'Column Break'
                    },
                    {
                        label: 'Fixed Cost Billing',
                        fieldname: 'fixed_cost_billing',
                        fieldtype: 'Check'
                    },
                    {
                        label: 'Estimated Hour',
                        fieldname: 'estimated_hour',
                        fieldtype: 'Float',
                        depends_on: 'eval:doc.fixed_cost_billing==1'
                    },
                    {
                        label: 'Type',
                        fieldname: 'type',
                        fieldtype: 'Link',
                        options: "Task Type"
                    },
                    {
                        label: 'Department',
                        fieldname: 'department',
                        fieldtype: 'Link',
                        options: "Department",
                        ignore_user_permissions: 1,
                    },
                    {
                        label: 'Is Billable',
                        fieldname: 'is_billable',
                        fieldtype: 'Check'
                    },
                    {
                        label: 'Parent Task',
                        fieldname: 'parent_task',
                        fieldtype: 'Link',
                        options: 'Task',
                        get_query: function () {
                            return {
                                filters: {
                                    is_group: 1
                                }
                            };
                        }
                    },
                    {
                        label: 'Employee Group',
                        fieldname: 'employee_group',
                        fieldtype: 'Link',
                        options: "Employee Group",
                        ignore_user_permissions: 1,
                        reqd: 1
                    },
                    {
                        label: 'Primary Consultant',
                        fieldname: 'primary_consultant',
                        fieldtype: 'Link',
                        options: "Employee",
                        ignore_user_permissions: 1,
                        reqd: 1
                    },
                    // {
                    //     label: 'Actual Time',
                    //     fieldname: 'actual_time',
                    //     fieldtype: 'Float'
                    // }
                ],
                size: 'extra-large',
                primary_action_label: 'Submit',
                primary_action(values) {
                    console.log(values);

                    frappe.call({
                        method: "nextproject.api.custom_submit_hd_ticket",
                        args: {
                            values: values,
                            doc:frm.doc.name

                        },
                        callback: function (r) {
                            if (!r.exc) {
                                frm.reload_doc();
                            }
                        }
                    });
                    console.log("api getting called");
                    d.hide();
                }
            });

            d.show();
        }, __("Create"));
        
        
        frm.add_custom_button('Fetch Tasks', () => {
            fetch_and_display_tasks(frm);


        }, __("Actions"));
        
        
        
    }
});

    function fetch_and_display_tasks(frm) {
        frappe.call({
            method: "nextproject.custom_hd_ticket.get_linked_tasks",
            args: {
                doc: frm.doc.subject
            },
            callback: function(r) {
                if (r.message) {
                    frm.clear_table('custom_helpdesk_task_information');

                    r.message.forEach(task => {
                        let new_row = frm.add_child('custom_helpdesk_task_information');
                        new_row.task_id = task.name;
                        new_row.status = task.status;
                        new_row.primary_consultant = task.primary_consultant_name;
                        new_row.expected_end_date = task.exp_end_date;
                        new_row.expected_time = task.expected_time;
                    });

                    frm.refresh_field('custom_helpdesk_task_information');
                    frm.save()
                }
            }
        });
    }  
