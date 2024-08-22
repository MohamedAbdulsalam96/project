// frappe.ui.form.on('Sales Order', {


//     refresh:function(frm){
//     frappe.model.get_value('Scope of Supply', {"sales_order":frm.doc.name,"docstatus":1},"name",
//     function(d) {
//         if(!d.name && frm.doc.docstatus==1){
//         cur_frm.add_custom_button(__('Scope Of Supply'), function() {
//             console.log(frm.doc.grand_total)
//             var x=frm.doc.grand_total
//             frappe.new_doc("Scope of Supply", {
//                 "sales_order":frm.doc.name,
//                 'customer':frm.doc.customer,
//                 'project_cost':frm.doc.grand_total,
//                 'biling_address':frm.doc.customer_address,
//                 'shipping_address':frm.doc.shipping_address_name,
//                 "currency":frm.doc.currency
//             })
            
//         }, __('Create'))
//         }
//         })
//     if(frm.doc.docstatus==1){
//         cur_frm.add_custom_button(__("Request For Quotation"), function() {
//             frm.call({
//                 method:"nextproject.nextproject.custom_sales_order.create_request_for_quotation",
//                 args:{
//                     name:frm.doc.name
//                 },
//                 callback: function(r) {
//                     if(r.message){
                        
//                         frappe.throw("Request for Quotation Created")
//                     }
                    
//                 }
                
//             });
//         }, __('Create'))
//     }
       
    
//     },
   
// })
