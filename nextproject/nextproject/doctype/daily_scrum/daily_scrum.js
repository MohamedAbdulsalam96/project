// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Scrum', {

    setup:function(frm){
        
        if(frm.doc.status=="Working"){
            frm.fields_dict.team_scrum.grid.update_docfield_property(
                'update_status',
                'options',
                ["Open", "Pending Review","Cancelled","Completed"]
            ); 
        }
            frm.refresh_field("team_scrum")
    },

    refresh: function(frm) {
        frm.fields_dict.team_scrum.grid.wrapper.find('.grid-add-row').hide();
        frm.fields_dict.team_scrum.grid.wrapper.find('.grid-remove-rows').hide()
        frm.fields_dict.follow_up_scrum_items.grid.wrapper.find('.grid-add-row').hide()
        let b=document.querySelectorAll('.btn-open-row')
        b.forEach((elm)=>{
            elm.onclick=()=>{
                let a=document.querySelectorAll(".grid-delete-row")
                a.forEach((elm2)=>{
                    elm2.style.display='none'
                });
            }
        })
        
        frm.fields_dict.follow_up_scrum_items.grid.wrapper.find('.grid-remove-rows').hide()

        frm.fields_dict['morning_scrum'].get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ['type', '=', "Morning"],
                    ["date","=",frm.doc.date],
                    ["docstatus","=",1],
                    ["team","=",frm.doc.team]


                ]
            };
        };
        frm.set_query("timesheet", "follow_up_scrum_items", function(doc,cdt,cdn) {
            let child = locals[cdt][cdn]
            return {
                query:"nextproject.nextproject.doctype.daily_scrum.daily_scrum.task_query",
                filters: {
                     "employee": child.member,
                     "from_date":frm.doc.date,
                     "task":child.current_task
                }
            };
        });
        frm.set_query("next_task", "follow_up_scrum_items", function(doc, cdt, cdn) {
            let child = locals[cdt][cdn];
            return {
                filters: {
                    'primary_consultant': child.member
                }
            };
        });
        
        frm.set_query("current_task", "team_scrum", function(doc, cdt, cdn) {
            let child = locals[cdt][cdn];
            return {
                filters: {
                    'primary_consultant': child.member
                }
            };
        });
    },
    get_team_details: function(frm) {
        frappe.call({
            method: "morning_data",
            doc: frm.doc,
            callback: function() {
                frm.refresh_field("team_scrum");
            }
        }); 
    },
	get_lines: function(frm) {
        frappe.call({
            method: "evening_data",
            doc: frm.doc,
            callback: function() {
                frm.refresh_field("lead");
				frm.refresh_field("lead_name");
				frm.refresh_field("follow_up_scrum_items");
            }
        });
    },
    team: function(frm) {
        frappe.call({
            method: "team_filters",
            doc: frm.doc,
            callback: function(r) {
                
                var employee_ids = r.message || [];
                frm.fields_dict['team_mebers'].get_query = function(doc, cdt, cdn) {
                    return {
                        filters: { "employee": ["in", employee_ids] }
                    };
                };
                frm.clear_table("team_mebers");
                employee_ids.forEach(function(element) {
                    var new_row = frm.add_child("team_mebers");
                    new_row.employee = element;
                });
                frm.refresh_field("team_mebers");
            }
        });
    },
    morning_scrum:function(frm) {
        frappe.call({
            method: "evening_team_filters",
            doc: frm.doc,
            callback: function(r) {
                var employee_members= r.message || [];
                frm.clear_table("team_mebers");
                employee_members.forEach(function(element) {
                    var new_row = frm.add_child("team_mebers");
                    new_row.employee = element;
                });
                frm.refresh_field("team_mebers");
            }
        });
    },
    
})    

frappe.ui.form.on('Daily Scrum Item', {
change_team:function(frm,cdt,cdn){
    console.log("change team working")
    let child=locals[cdt][cdn]
    if(child.change_team){
    // frm.selected_doc.ignore_timesheet_check=1
    child.ignore_timesheet_check=1
    frm.refresh_field("team_scrum")
    
    }
},
task_details:function(frm,cdt,cdn){
    let child = locals[cdt][cdn];
    frappe.call({
        method:"task_details",
        doc: frm.doc,
        args:{
            task:child.current_task
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
                                task:child.current_task
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
   

    
},
working:function(frm,cdt,cdn){
    let child=locals[cdt][cdn]
    frappe.call({
        method: "state_change",
        doc: frm.doc,
        args:{
            status:"Working",
            task:child.current_task
        },
        callback: function() {

            child.status="Working"
            frm.refresh_field("team_scrum");
        }
    });
},
open:function(frm,cdt,cdn){
    let child=locals[cdt][cdn]
    frappe.call({
        method: "state_change",
        doc: frm.doc,
        args:{
            status:"Open",
            task:child.current_task
        },
        callback: function() {

            child.status="Open"
            frm.refresh_field("team_scrum");
        }
    });
},


cancelled:function(frm,cdt,cdn){
    let child=locals[cdt][cdn]
    frappe.call({
        method: "state_change",
        doc: frm.doc,
        args:{
            status:"Cancelled",
            task:child.current_task
        },
        callback: function() {
            child.status="Cancelled"

            frm.refresh_field("team_scrum");
        }
    });
},
completed:function(frm,cdt,cdn){
    let child=locals[cdt][cdn]
    frappe.call({
        method: "state_change",
        doc: frm.doc,
        args:{
            status:"Completed",
            task:child.current_task
        },
        callback: function() {
            child.status="Completed"
            child.ignore_timesheet_check=1
            child.on_track=1
            frm.refresh_field("team_scrum");
        }
    });
},
pending_review:function(frm,cdt,cdn){
    let child=locals[cdt][cdn]
    frappe.call({
        method: "state_change",
        doc: frm.doc,
        args:{
            status:"Pending Review",
            task:child.current_task
        },
        callback: function() {
            child.status="Pending Review"

            frm.refresh_field("team_scrum");
        }
    });
}

});
frappe.ui.form.on('Follow up Scrum Items', {
    task_details:function(frm,cdt,cdn){
        let child = locals[cdt][cdn];
        frappe.call({
            method:"task_details",
            doc: frm.doc,
            args:{
                task:child.current_task
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
                                    task:child.current_task
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
    
        
    },

    working:function(frm,cdt,cdn){
        let child=locals[cdt][cdn]
        frappe.call({
            method: "state_change",
            doc: frm.doc,
            args:{
                status:"Working",
                task:child.current_task
            },
            callback: function() {
    
                child.status="Working"
                frm.refresh_field("follow_up_scrum_items");
            }
        });
    },
    open:function(frm,cdt,cdn){
        let child=locals[cdt][cdn]
        frappe.call({
            method: "state_change",
            doc: frm.doc,
            args:{
                status:"Open",
                task:child.current_task
            },
            callback: function() {
    
                child.status="Open"
                frm.refresh_field("follow_up_scrum_items");
            }
        });
    },
    
    
    cancelled:function(frm,cdt,cdn){
        let child=locals[cdt][cdn]
        frappe.call({
            method: "state_change",
            doc: frm.doc,
            args:{
                status:"Cancelled",
                task:child.current_task
            },
            callback: function() {
                child.status="Cancelled"
    
                frm.refresh_field("follow_up_scrum_items");
            }
        });
    },
    completed:function(frm,cdt,cdn){
        let child=locals[cdt][cdn]
        frappe.call({
            method: "state_change",
            doc: frm.doc,
            args:{
                status:"Completed",
                task:child.current_task
            },
            callback: function() {
                child.status="Completed"
                child.ignore_timesheet_check=1
                child.on_track=1
                frm.refresh_field("follow_up_scrum_items");
            }
        });
    },
    pending_review:function(frm,cdt,cdn){
        let child=locals[cdt][cdn]
        frappe.call({
            method: "state_change",
            doc: frm.doc,
            args:{
                status:"Pending Review",
                task:child.current_task
            },
            callback: function() {
                child.status="Pending Review"
    
                frm.refresh_field("follow_up_scrum_items");
            }
        });
    }
    
    });
    
