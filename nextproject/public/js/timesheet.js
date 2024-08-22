// // Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// // License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Timesheet", {
  setup:function(frm){
     
            frm.ignore_doctypes_on_cancel_all = ['Daily Scrum'];
    
      
		frm.fields_dict['time_logs'].grid.get_field('task').get_query = function(frm, cdt, cdn) {
			var child = locals[cdt][cdn];
			return{
				filters: {
					'project': child.project,
					'status': ["!=", "Cancelled"],
          			'is_group': 0
				}
			};
		};
            frm.set_query("project", "time_logs", function() {
			return {
                        filters: {
                              'company': frm.doc.company,
                              'status': ["!=", "Cancelled"]
                        }
			}
		});

  	},
  before_save:function(frm){
     
      let base_currency = frappe.defaults.get_global_default('currency');
      if (base_currency != frm.doc.currency) {
            frappe.call({
                  method: "erpnext.setup.utils.get_exchange_rate",
                  args: {
                        from_currency: frm.doc.currency,
                        to_currency: base_currency
                  },
                  callback: function(r) {
                        if (r.message) {
                              frm.set_value('exchange_rate', flt(r.message));
                              frm.set_df_property("exchange_rate", "description", "1 " + frm.doc.currency + " = [?] " + base_currency);
                        }
                  }
            });
      }
     
	
    }

});

frappe.ui.form.on('Timesheet', {
 validate: function(frm) {
      frm.doc.time_logs.forEach(function(row) {
      validate_project_status(frm, row);
      validate_task_status(frm, row);
    });
     }
     });
     
     function validate_project_status(frm, row) {
       if (row.project) {
      frappe.call({
      method: 'frappe.client.get_value',
      args: {
      'doctype': 'Project',
      'filters': {'name': row.project},
     'fieldname': 'status'
      },
     async: false,
      callback: function(r) {
      if (r.message) {
      const project_status = r.message.status;
      if (project_status !== 'Open') {
      frappe.msgprint(__('Project "{0}" is not in an "Open" status', [row.project]));
     frappe.validated = false;
      }
      }
      }
      });
      }
     }
     
     function validate_task_status(frm, row) {
      if (row.task) {
      frappe.call({
            method: 'frappe.client.get_value',
            args: {
            'doctype': 'Task',
            'filters': {'name': row.task},
            'fieldname': 'status'
            },
            async: false,
      callback: function(r) {
            if (r.message) {
                  const task_status = r.message.status;
                  const valid_statuses = ['Open', 'Working', 'Pending Review', 'Overdue'];
            if (!valid_statuses.includes(task_status)) {
                  frappe.msgprint(__('Task "{0}" status must be "Open", "Working", "Pending Review", or "Overdue"', [row.task]));
            frappe.validated = false;
      }
      }
      }
     });
     }
     }
     
           


          
