// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Revenue Projection', {
    // refresh: function (frm) {
    //     frm.set_query('project', function () {
    //         return {
    //             filters: [
    //                 ['status', '=', 'Open'],
    //                 ['billing_based_on', 'in',['Timesheet Based','Milestone Based','Fixed Recurring','Allocation Based']]
    //             ]
    //         };
    //     });
    // },
    // frm.set_query('task', function() {
    //     let selected_project = frm.doc.project;
    //     if (!selected_project) {
    //         return {
    //             filters: []
    //         };
    //     }
    //     return {
    //         filters: [
    //             ['project', '=', selected_project],
    //             ['expected_start_date', '<=', frappe.datetime.now_date()],
    //             ['expected_end_date', '>=', frappe.datetime.now_date()]
    //         ]
    //     };
    // });

    // project: function (frm) {
    //     console.log('clicked')
    //     frappe.call({
    //         method: "get_data",
    //         doc: frm.doc,
    //         callback: function (response) {
    //             console.log(response.message);
    //             if (response.message){
    //                 console.log("list return : ",response.message)
    //                 frm.set_value('last_billing_date', response.message[0]);
    //                 frm.set_value('next_billing_date', response.message[1]);
                    
    //             }

    //         }
    //     })
    // }

});







// project: function (frm) {
//     console.log('clicked')
//     frappe.call({
//         method: "get_data",
//         doc: frm.doc,
//         callback: function (response) {
//             console.log(response.message);
//             if (response.message){
//                 frm.set_query("task", function(frm){
//                     return{
//                         filters:[['name','in', response.message]]
//                     }
//                 })
                
//             }

//         }
//     })
// }