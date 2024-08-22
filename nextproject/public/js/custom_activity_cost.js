frappe.ui.form.on("Activity Cost",{



    employee:function(frm){
        frappe.call({
            method:"nextproject.event_activity_cost.activity_cost",
            args:{
                "employee":frm.doc.employee
            },
            callback:function(r){
                if(r.message){
                    frm.set_value("costing_rate",r.message)
                    frm.refresh_field("costing_rate")
                }

            }


        })
    }

})