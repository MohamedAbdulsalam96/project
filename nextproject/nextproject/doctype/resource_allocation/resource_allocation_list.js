frappe.listview_settings['Resource Allocation'] = {

    onload: function(list_view) {

		list_view.page.add_inner_button(__("Fetch Allocation"), function() { 
            
          let  d = new frappe.ui.Dialog({
                title: 'Fetch Allocation',
                    fields:[
                    {
                        label: 'From Date',
                        fieldname: 'exp_start_date',
                        fieldtype: 'Date',
                        reqd:1

                    },
                    {
                        label: 'To Date',
                        fieldname: 'exp_end_date',
                        fieldtype: 'Date',
                        reqd:1
                    },
                    {
                        label: 'Primary Consultant',
                        fieldname: 'primary_consultant',
                        fieldtype: 'Link',
                        options:'Employee'
                    },
                    {
                        label:'Task',
                        fieldname:'task',
                        fieldtype:'Link',
                        options:'Task',
                        get_query: () => {
                            return {
                                filters: {
                                    'is_group': 0,
                                    'is_template':0,
                                    'status':["not in",["Template","Completed","Cancelled"]]

                                    
                                }
                            };
                        }
                    },
                    {
                        label:'Project',
                        fieldname:'project',
                        fieldtype:'Link',
                        options:'Project'

                    }
                    
                ],
                primary_action_label: 'Submit',
                primary_action(values) {
                    frappe.call({
                        method:"nextproject.nextproject.doctype.resource_allocation.resource_allocation.create_resource_allocation",
                        args:{
                            'values':values
                            
                        },
                        callback:function(r){
                            frm.refresh()
                        }
                    })
                    d.hide();
    }
                
            });
            d.show();
            
         })
	},

	add_button(name, type, action, wrapper_class=".page-actions") {
		const button = document.createElement("button");
		button.classList.add("btn", "btn-" + type, "btn-sm", "ml-2");
		button.innerHTML = name;
		button.onclick = action;
		document.querySelector(wrapper_class).prepend(button);
	},

}

