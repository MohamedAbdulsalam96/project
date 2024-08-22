// frappe.ui.form.on('Quotation', {


//     onload:function(frm){
//         frm.remove_custom_button("Sales Order", 'Create');
//         if(!frm.doc.scope_of_supply){
//             cur_frm.add_custom_button(__('Scope Of Supply'), function() {
//                 console.log(frm.doc.grand_total)
//                 var x=frm.doc.grand_total
//                 frappe.new_doc("Scope of Supply", {
//                     "quotation":frm.doc.name,
//                     "quotation_to":frm.doc.quotation_to,
//                     'customer':frm.doc.party_name,
//                     'project_cost':x,
//                     'biling_address':frm.doc.customer_address,
//                     "shipping_full_address":frm.doc.shipping_address,
//                     "billing_full_address":frm.doc.address_display,
//                     'shipping_address':frm.doc.shipping_address_name,
//                     "currency":frm.doc.currency
//                 })
                
//             }, __('Create'))
//         }
       
    
//     },
   
// })
