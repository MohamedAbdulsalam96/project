frappe.ui.form.on("Task", {
	setup: function (frm) {
        frm.set_query("project", function() {
			return {
				"filters": {
					'company': frm.doc.company,
					'status': ["!=", "Cancelled"],
				}
			}
		});
		frm.set_query("primary_consultant", function() {
			return {
				"filters": {
					'status': 'Active'
				}
			}
		});
		frm.set_query("project_lead", function() {
			return {
				"filters": {
					'status': 'Active'
				}
			}
		});
    },
    refresh:function(frm){
        frm.set_query("issue", function() {
			return {
				"filters": {
                    'status': ["!=", "Cancelled"],
                    'project':frm.doc.project
				}
			}
		});
    }, 
	after_save:function(frm){
		frm.call({
			method: "nextproject.task.status",
			args: { task: frm.doc.name },
		}).then((r) => {
				if (r.message === true) {
				console.log("Heloooo#########");
			}
		});
		frm.doc.custom_previous_exp_date = frm.doc.exp_end_date;
	},
})