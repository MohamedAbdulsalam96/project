// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Task Completion', {
	refresh: function(frm) {
		frm.add_custom_button(__('Fetch Task'),function(){	
			frappe.call({
			method:"fetch_task_details",
			doc: frm.doc,
			callback:function(r){
				if (r.message){
					frm.refresh_fields("task_new")
					frm.refresh_fields("task_pending_review")
					frm.refresh_fields("task_overdue")
					frm.refresh_fields("task_open")
					frm.refresh_fields("task_working")
					frm.refresh()
				}
			}
		})
	}).addClass("btn-primary");
	
frm.set_df_property('task_new', 'cannot_add_rows', 1);
frm.set_df_property('task_pending_review', 'cannot_add_rows', 1);
frm.set_df_property('task_overdue', 'cannot_add_rows', 1);
frm.set_df_property('task_open', 'cannot_add_rows', 1);
frm.set_df_property('task_working', 'cannot_add_rows', 1);
frm.disable_save();
	},
	primary_consultant: function(frm){
		if (frm.doc.task_pending_review || frm.doc.task_overdue)
		{ 
			frm.doc.task_new = ""
			frm.doc.task_overdue = ""
			frm.doc.task_pending_review = ""
			frm.doc.task_open = "" 
			frm.doc.task_working = ""
			frm.doc.task_completed = ""
			frm.refresh_fields("task_new")
			frm.refresh_fields("task_overdue")
			frm.refresh_fields("task_pending_review")
			frm.refresh_fields("task_open")
			frm.refresh_fields("task_working")
			frm.refresh_fields("task_completed")
			frm.refresh()
		} 
	},
	employee_group: function(frm){
		if (!frm.doc.employee_group)
		{
			frm.doc.primary_consultant = "";
			frm.doc.primary_consultant_name = "";
			frm.refresh_fields("primary_consultant")
			frm.refresh_fields("primary_consultant_name")
		}
		if (frm.doc.task_completed || frm.doc.task_new || frm.doc.task_pending_review || frm.doc.task_overdue || frm.doc.task_open || frm.doc.task_working)
		{
			frm.doc.task_new = ""
			frm.doc.task_overdue = ""
			frm.doc.task_pending_review = ""
			frm.doc.task_open = ""
			frm.doc.task_working = ""
			frm.doc.task_completed = ""
			frm.refresh_fields("task_new")
			frm.refresh_fields("task_overdue")
			frm.refresh_fields("task_pending_review")
			frm.refresh_fields("task_open")
			frm.refresh_fields("task_working")
			frm.refresh_fields("task_completed")
			frm.refresh()
		} 
	}
});

frappe.ui.form.on('Task New',{
	open: function(frm, cdt, cdn){
		var child_row = locals[cdt][cdn];
		console.log(child_row)
			frappe.call({
			method:"nextproject.nextproject.doctype.task_completion.task_completion.new_to_open",
			args: {          
				doc_id: child_row.task_id
			},
			callback:function(r){
				if (r.message){
					frappe.call({
						method:"fetch_task_details",
						doc: frm.doc,
						callback:function(r){
							if (r.message){
								frm.refresh_fields("task_new")
								frm.refresh_fields("task_pending_review")
								frm.refresh_fields("task_overdue")
								frm.refresh_fields("task_open")
								frm.refresh_fields("task_working")
								frm.refresh_fields("task_completed")
								frm.refresh()
							}
						}
					})
					frm.refresh_fields("task_new")
				}
			}
		})
	},
	show_details:function(frm,cdt,cdn){
		let child = locals[cdt][cdn];
    frappe.call({
        method:"task_details",
        doc: frm.doc,
        args:{
            task:child.task_id
        },
        callback:function(r){
            if (r.message){
      
                let d = new frappe.ui.Dialog({
                    title: 'Enter details',
                    fields: [
                       
                        {
                            label: 'Description',
                            fieldname: 'description',
                            fieldtype: 'Text Editor',
                            default:r.message[0],
                            read_only:1
                        },
                        {
                            label: 'Checklist Items',
                            fieldname: 'checklist_items',
                            fieldtype: 'Table',
                            fields: [
                                {
                                    label: __('Particulars'),
                                    fieldname: 'particulars',
                                    fieldtype: 'Data',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Expected End Date'),
                                    fieldname: 'expected_end_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Completed'),
                                    fieldname: 'completed',
                                    fieldtype: 'Check',
                                    in_list_view: 1
                                                                     
                                },
                                {
                                    label: __('Completion Date'),
                                    fieldname: 'completion_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    mandatory_depends_on:"eval:doc.completed == \"1\""
                                },
                                {
                                    label: __('Hours'),
                                    fieldname: 'hours',
                                    fieldtype: 'Duration',
                                    in_list_view: 1,
                                    reqd:1
                                }

                                
                            ],
                            data: r.message[1],
                            
                        }

                    ],
                    size: 'extra-large', // small, large, extra-large 
                    primary_action_label: 'Update/Close',
                    primary_action(values) {
                        frappe.call({
                            "method":"update_task",
                            doc: frm.doc,
                            args:{
                                values:values,
                                task:child.task_id
                            },
                            callback:function(r){
                                

                            }


                        })
                        d.hide();
                    }
                });
                d.show();
            }
        }
	
	})
}
});
frappe.ui.form.on('Task Pending Review',{
	complete: function(frm, cdt, cdn){
		var child_row = locals[cdt][cdn];
			frappe.call({
			method:"nextproject.nextproject.doctype.task_completion.task_completion.pending_review_to_complete",
			doc_id:child_row.task_id,
			args: {          
				doc_id: child_row.task_id
			},
			callback:function(r){
				if (r.message){
					frappe.call({
						method:"fetch_task_details",
						doc: frm.doc,
						callback:function(r){
							if (r.message){
								frm.refresh_fields("task_new")
								frm.refresh_fields("task_pending_review")
								frm.refresh_fields("task_overdue")
								frm.refresh_fields("task_open")
								frm.refresh_fields("task_working")
								frm.refresh_fields("task_completed")
								frm.refresh()
							}
						}
					})
					frm.refresh_fields("task_pending_review")
				}
			}
		})
	},
	show_details:function(frm,cdt,cdn){
		let child = locals[cdt][cdn];
    frappe.call({
        method:"task_details",
        doc: frm.doc,
        args:{
            task:child.task_id
        },
        callback:function(r){
            if (r.message){
      
                let d = new frappe.ui.Dialog({
                    title: 'Enter details',
                    fields: [
                       
                        {
                            label: 'Description',
                            fieldname: 'description',
                            fieldtype: 'Text Editor',
                            default:r.message[0],
                            read_only:1
                        },
                        // {
                        //     label: 'Checklist',
                        //     fieldname: 'checklist',
                        //     fieldtype: 'Tab Break'
                            
                        // },
                        {
                            label: 'Checklist Items',
                            fieldname: 'checklist_items',
                            fieldtype: 'Table',
                            fields: [
                                {
                                    label: __('Particulars'),
                                    fieldname: 'particulars',
                                    fieldtype: 'Data',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Expected End Date'),
                                    fieldname: 'expected_end_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Completed'),
                                    fieldname: 'completed',
                                    fieldtype: 'Check',
                                    in_list_view: 1
                                                                     
                                },
                                {
                                    label: __('Completion Date'),
                                    fieldname: 'completion_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    mandatory_depends_on:"eval:doc.completed == \"1\""
                                },
                                {
                                    label: __('Hours'),
                                    fieldname: 'hours',
                                    fieldtype: 'Duration',
                                    in_list_view: 1,
                                    reqd:1
                                }

                                
                            ],
                            data: r.message[1],
                            
                        }

                    ],
                    size: 'extra-large', // small, large, extra-large 
                    primary_action_label: 'Update/Close',
                    primary_action(values) {
                        frappe.call({
                            "method":"update_task",
                            doc: frm.doc,
                            args:{
                                values:values,
                                task:child.task_id
                            },
                            callback:function(r){
                                

                            }


                        })
                        d.hide();
                    }
                });
                d.show();
            }
        }
	
	})
}
});
frappe.ui.form.on('Task Overdue',{
	revert: function(frm, cdt, cdn){
		var child_row = locals[cdt][cdn];
		console.log(child_row)
			frappe.call({
			method:"nextproject.nextproject.doctype.task_completion.task_completion.overdue_to_working",
			doc_id:child_row.task_id,
			args: {          
				doc_id: child_row.task_id
			},
			callback:function(r){
				if (r.message){
					frappe.call({
						method:"fetch_task_details",
						doc: frm.doc,
						callback:function(r){
							if (r.message){
								frm.refresh_fields("task_new")
								frm.refresh_fields("task_pending_review")
								frm.refresh_fields("task_overdue")
								frm.refresh_fields("task_open")
								frm.refresh_fields("task_working")
								frm.refresh_fields("task_completed")
								frm.refresh()
							}
						}
					})
					frm.refresh_fields("task_overdue")
				}
		}
		})
	},
	show_details:function(frm,cdt,cdn){
		let child = locals[cdt][cdn];
    frappe.call({
        method:"task_details",
        doc: frm.doc,
        args:{
            task:child.task_id
        },
        callback:function(r){
            if (r.message){
      
                let d = new frappe.ui.Dialog({
                    title: 'Enter details',
                    fields: [
                       
                        {
                            label: 'Description',
                            fieldname: 'description',
                            fieldtype: 'Text Editor',
                            default:r.message[0],
                            read_only:1
                        },
                        // {
                        //     label: 'Checklist',
                        //     fieldname: 'checklist',
                        //     fieldtype: 'Tab Break'
                            
                        // },
                        {
                            label: 'Checklist Items',
                            fieldname: 'checklist_items',
                            fieldtype: 'Table',
                            fields: [
                                {
                                    label: __('Particulars'),
                                    fieldname: 'particulars',
                                    fieldtype: 'Data',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Expected End Date'),
                                    fieldname: 'expected_end_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Completed'),
                                    fieldname: 'completed',
                                    fieldtype: 'Check',
                                    in_list_view: 1
                                                                     
                                },
                                {
                                    label: __('Completion Date'),
                                    fieldname: 'completion_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    mandatory_depends_on:"eval:doc.completed == \"1\""
                                },
                                {
                                    label: __('Hours'),
                                    fieldname: 'hours',
                                    fieldtype: 'Duration',
                                    in_list_view: 1,
                                    reqd:1
                                }

                                
                            ],
                            data: r.message[1],
                            
                        }

                    ],
                    size: 'extra-large', // small, large, extra-large 
                    primary_action_label: 'Update/Close',
                    primary_action(values) {
                        frappe.call({
                            "method":"update_task",
                            doc: frm.doc,
                            args:{
                                values:values,
                                task:child.task_id
                            },
                            callback:function(r){
                                

                            }


                        })
                        d.hide();
                    }
                });
                d.show();
            }
        }
	
	})
}
});
frappe.ui.form.on('Task Open',{
	working: function(frm, cdt, cdn){
		var child_row = locals[cdt][cdn];
			frappe.call({
			method:"nextproject.nextproject.doctype.task_completion.task_completion.open_to_working",
			doc_id:child_row.task_id,
			args: {          
				doc_id: child_row.task_id
			},
			callback:function(r){
				if (r.message){
					frappe.call({
						method:"fetch_task_details",
						doc: frm.doc,
						callback:function(r){
							if (r.message){
								frm.refresh_fields("task_new")
								frm.refresh_fields("task_pending_review")
								frm.refresh_fields("task_overdue")
								frm.refresh_fields("task_open")
								frm.refresh_fields("task_working")
								frm.refresh_fields("task_completed")
								frm.refresh()
							}
						}
					})
					frm.refresh_fields("task_open")
				}
		}
		})
	},
	show_details:function(frm,cdt,cdn){
		let child = locals[cdt][cdn];
    frappe.call({
        method:"task_details",
        doc: frm.doc,
        args:{
            task:child.task_id
        },
        callback:function(r){
            if (r.message){
      
                let d = new frappe.ui.Dialog({
                    title: 'Enter details',
                    fields: [
                       
                        {
                            label: 'Description',
                            fieldname: 'description',
                            fieldtype: 'Text Editor',
                            default:r.message[0],
                            read_only:1
                        },
                        // {
                        //     label: 'Checklist',
                        //     fieldname: 'checklist',
                        //     fieldtype: 'Tab Break'
                            
                        // },
                        {
                            label: 'Checklist Items',
                            fieldname: 'checklist_items',
                            fieldtype: 'Table',
                            fields: [
                                {
                                    label: __('Particulars'),
                                    fieldname: 'particulars',
                                    fieldtype: 'Data',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Expected End Date'),
                                    fieldname: 'expected_end_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Completed'),
                                    fieldname: 'completed',
                                    fieldtype: 'Check',
                                    in_list_view: 1
                                                                     
                                },
                                {
                                    label: __('Completion Date'),
                                    fieldname: 'completion_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    mandatory_depends_on:"eval:doc.completed == \"1\""
                                },
                                {
                                    label: __('Hours'),
                                    fieldname: 'hours',
                                    fieldtype: 'Duration',
                                    in_list_view: 1,
                                    reqd:1
                                }

                                
                            ],
                            data: r.message[1],
                            
                        }

                    ],
                    size: 'extra-large', // small, large, extra-large 
                    primary_action_label: 'Update/Close',
                    primary_action(values) {
                        frappe.call({
                            "method":"update_task",
                            doc: frm.doc,
                            args:{
                                values:values,
                                task:child.task_id
                            },
                            callback:function(r){
                                

                            }


                        })
                        d.hide();
                    }
                });
                d.show();
            }
        }
	
	})
}
});
frappe.ui.form.on('Task Working',{
	review: function(frm, cdt, cdn){
		var child_row = locals[cdt][cdn];
			frappe.call({
			method:"nextproject.nextproject.doctype.task_completion.task_completion.working_to_preview",
			doc_id:child_row.task_id,
			args: {          
				doc_id: child_row.task_id
			},
			callback:function(r){
				if (r.message){
					frappe.call({
						method:"fetch_task_details",
						doc: frm.doc,
						callback:function(r){
							if (r.message){
								frm.refresh_fields("task_new")
								frm.refresh_fields("task_pending_review")
								frm.refresh_fields("task_overdue")
								frm.refresh_fields("task_open")
								frm.refresh_fields("task_working")
								frm.refresh_fields("task_completed")
								frm.refresh()
							}
						}
					})
					frm.refresh_fields("task_working")
				}
		}
		})
	},
	show_details:function(frm,cdt,cdn){
		let child = locals[cdt][cdn];
    frappe.call({
        method:"task_details",
        doc: frm.doc,
        args:{
            task:child.task_id
        },
        callback:function(r){
            if (r.message){
      
                let d = new frappe.ui.Dialog({
                    title: 'Enter details',
                    fields: [
                       
                        {
                            label: 'Description',
                            fieldname: 'description',
                            fieldtype: 'Text Editor',
                            default:r.message[0],
                            read_only:1
                        },
                        // {
                        //     label: 'Checklist',
                        //     fieldname: 'checklist',
                        //     fieldtype: 'Tab Break'
                            
                        // },
                        {
                            label: 'Checklist Items',
                            fieldname: 'checklist_items',
                            fieldtype: 'Table',
                            fields: [
                                {
                                    label: __('Particulars'),
                                    fieldname: 'particulars',
                                    fieldtype: 'Data',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Expected End Date'),
                                    fieldname: 'expected_end_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    reqd:1
                                },
                                {
                                    label: __('Completed'),
                                    fieldname: 'completed',
                                    fieldtype: 'Check',
                                    in_list_view: 1
                                                                     
                                },
                                {
                                    label: __('Completion Date'),
                                    fieldname: 'completion_date',
                                    fieldtype: 'Date',
                                    in_list_view: 1,
                                    mandatory_depends_on:"eval:doc.completed == \"1\""
                                },
                                {
                                    label: __('Hours'),
                                    fieldname: 'hours',
                                    fieldtype: 'Duration',
                                    in_list_view: 1,
                                    reqd:1
                                }

                                
                            ],
                            data: r.message[1],
                            
                        }

                    ],
                    size: 'extra-large', // small, large, extra-large 
                    primary_action_label: 'Update/Close',
                    primary_action(values) {
                        frappe.call({
                            "method":"update_task",
                            doc: frm.doc,
                            args:{
                                values:values,
                                task:child.task_id
                            },
                            callback:function(r){
                                

                            }


                        })
                        d.hide();
                    }
                });
                d.show();
            }
        }
	
	})
}
});
frappe.ui.form.on('Task Working',{
	completed: function(frm, cdt, cdn){
		var child_row = locals[cdt][cdn];
		console.log(child_row)
			frappe.call({
			method:"nextproject.nextproject.doctype.task_completion.task_completion.pending_review_to_complete",
			doc_id:child_row.task_id,
			args: {          
				doc_id: child_row.task_id
			},
			callback:function(r){
				if (r.message){
					frappe.call({
						method:"fetch_task_details",
						doc: frm.doc,
						callback:function(r){
							if (r.message){
								frm.refresh_fields("task_new")
								frm.refresh_fields("task_pending_review")
								frm.refresh_fields("task_overdue")
								frm.refresh_fields("task_open")
								frm.refresh_fields("task_working")
								frm.refresh_fields("task_completed")
								frm.refresh()
							}s
						}
					})
					frm.refresh_fields("task_completed")
				}
			}
		})
	}
});