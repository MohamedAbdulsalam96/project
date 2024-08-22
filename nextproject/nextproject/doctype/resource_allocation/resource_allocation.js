// Copyright (c) 2022, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Resource Allocation', {
    refresh: function(frm){

        frm.set_df_property('resource_allocation_items', 'cannot_add_rows', 1);
    }



});

frappe.ui.form.on('Resource Allocation Items', {
    // page.add_inner_button('New Post', () => new_post(), 'Make')
    split:function(frm,cdt,cdn){
        let child=locals[cdt][cdn]
        let d = new frappe.ui.Dialog({
            title: '      ',
            
            fields: [
               
                {

                    fieldtype: "Date",
                    label: __("Date"),
                    fieldname: "date",
                    default:new Date()
                    //options:"Task"

                },
                
                {

                    fieldtype: "Column Break",
                    fieldname: "column_break",

                },
                
                {

                    fieldtype: "Float",
                    label: __("Hours"),
                    fieldname: "hours",
                    default:child.allocation
                    // options: "Project"

                },
                

            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                frappe.call({
                    method: "nextproject.nextproject.doctype.resource_allocation.resource_allocation.split",
                    args:{
                        "values":values,
                        "date":frm.doc.date,
                        "hours":frm.doc.allocation,
                        "name":frm.doc.name,
                        "a":child.name,
                        "task":child.task,
                        "pc":frm.doc.primary_consultance
                    },
                    callback: function(r){
                        
                        cur_frm.refresh_field("allocation")

                    
                    }
                   
                });
                console.log('values^^^^^^^^^^^^',values.hours)
                console.log(values);
                d.hide();
            }
        });
        
        d.show();
    },

    move:function(frm,cdt,cdn){
        let child=locals[cdt][cdn]
        let d = new frappe.ui.Dialog({
            title: '      ',
            
            fields: [
               
                {

                    fieldtype: "Date",
                    label: __("Date"),
                    fieldname: "date",
                    default:new Date()
                    //options:"Task"

                },
                
                {

                    fieldtype: "Column Break",
                    fieldname: "column_break",

                },
                
                {

                    fieldtype: "Read Only",
                    label: __("Hours"),
                    fieldname: "hours",
                    default:child.allocation
                    // options: "Project"

                },
                

            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                frappe.call({
                    method: "nextproject.nextproject.doctype.resource_allocation.resource_allocation.move",
                    args:{
                        "values":values,
                        "date":frm.doc.date,
                        "hours":frm.doc.allocation,
                        "name":frm.doc.name,
                        "a":child.name,
                        "task":child.task,
                        "pc":frm.doc.primary_consultance

                    },
                    callback:function(r){
                    if (r.message){
                        cur_frm.refresh();
                       
                    }
                }
                   
                });
                
                console.log("LLLLLLLLLLLLLLLLLLJ",values,date);
                d.hide();
            }
        });
        
        d.show();
    },

});