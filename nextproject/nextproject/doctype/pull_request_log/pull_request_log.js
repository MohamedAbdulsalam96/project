// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt
 
	 
frappe.ui.form.on('Pull Request Log', {
	refresh: function(frm) {
		if (frm.doc.state === 'open') {
			frm.add_custom_button(__('Close'), function(){
				frappe.call({
					doc: frm.doc,
					method:"close_document",
					callback:function(r){
						if (r.message){
						}
						frm.reload_doc();
					}
				});
			});
		}
		if (frm.doc.state === 'Closed' && frm.doc.merge_request_state === 'Open') {
			frm.add_custom_button(__('Open'), function(){
				frappe.call({
					doc: frm.doc,
					method:"close_document",
					callback:function(r){
						if (r.message){
						}
						frm.reload_doc();
					}
				});
			 
			});
		}
		if (frm.doc.state === 'open') {
			frm.add_custom_button(__('Merge'), function(){
				frappe.call({
					doc: frm.doc,
					method:"merge_pull_request",
					callback:function(r){
						if (r.message){
						}
						frm.reload_doc();
					}
				});
			 
			});
		}
		if (frm.doc.merge_request_state == 'Merged')
		{
			frm.toggle_enable('*', false);
		}
	}
});