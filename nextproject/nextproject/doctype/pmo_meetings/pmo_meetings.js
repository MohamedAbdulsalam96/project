// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('PMO Meetings', {
	
		refresh: function(frm) {

			if(frm.doc.status=="Completed" || frm.doc.status=="Cancelled"){
				var doctype = "PMO Meetings";

				frappe.get_meta(doctype).fields.forEach(function(d) {
					frm.set_df_property(d.fieldname, 'read_only', 1);

				})
		
			}
			frm.call({
				method:'get_matching_link_names',
				doc:frm.doc,
					callback: function(response) {
						if(response.message){

							console.log(response.message)
							cur_frm.fields_dict['pmo_meeting_attendees'].grid.get_field('contact_person').get_query = function(doc, cdt, cdn) {
								return {
									filters: [
												['name', 'in' , response.message]
									]
								}

								
							}
							frm.refresh_field("pmo_meeting_attendees")
						}
						

							}
					})
			if (frm.doc.__islocal) {
				
				frm.get_field('send_calendar_invite').$wrapper.hide();
	
			
				frm.get_field('invite_send').$wrapper.hide();
			} else {
				if(frm.doc.status!="Completed"){
				frm.add_custom_button(__('Completed'), function(){
					frm.set_value("status", "Completed");
				}, __("Status"));
				}
				if(frm.doc.status!="Cancelled"){
					frm.add_custom_button(__('Cancelled'), function(){
						frm.set_value("status", "Cancelled");
					}, __("Status"));
			    }
				
				frm.get_field('send_calendar_invite').$wrapper.show();
	
				
				frm.get_field('invite_send').$wrapper.show();
			}
			if (frm.doc.repeat_this_event == 0) {
				console.log("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
				frm.set_value("meeting_scheduled_time", "");
				frm.refresh_field("meeting_scheduled_time")
			}
			if (frm.doc.repeat_this_event == 0) {
				frm.set_value("meeting_scheduled_time", "");
				frm.refresh_field("meeting_scheduled_time");
			}
	},

	
	    onload:function(frm) {

			frm.set_query("project",function(){
				return{
					filters:{
						"status":"Open",
						"is_active":"Yes"
					}
				}
			});

			frm.set_query("meeting_host",function(){
				return{
					filters:{
						"enabled":1,
						"user_type":"System User"
					}
				}

			});

			frm.set_query("risk","pmo_meeting_risks",function(){
				return{
					filters:{
						"project":frm.doc.project,
						"status": ["in", ["Risk Reported", "In Progress"]]


					}
				}
			
			});

		

		},

		project:function(frm){
			frm.call({
				 method:'get_matching_link_names',
				 doc:frm.doc,
			callback: function(response) {
				if(response.message){

					console.log(response.message)
					cur_frm.fields_dict['pmo_meeting_attendees'].grid.get_field('contact_person').get_query = function(doc, cdt, cdn) {
                        return {
                            filters: [
                                       ['name', 'in' , response.message]
                            ]
                        }
                    }
					frm.refresh_field("pmo_meeting_attendees")
				}
				}
		   })
	   },
		date:function(frm){
		    
			frm.call({
				 method:'validate_date',
				 doc:frm.doc,
			callback: function(response) {
				if(response.message){
					frappe.msgprint('Past date not allowed');
					frm.set_value('date', "");
				 
				}
				else{
					pass
				}

				 }
		   })
	   },
	   	
		send_calendar_invite:function(frm){
			frm.call({
				method:'create_event',
				doc:frm.doc,
			callback: function(response) {
					if (response.message) {
						frappe.msgprint('Calendar event created successfully.');
				} 	else {
						frappe.msgprint('Failed to create calendar event.');
					}
				}
			})
		// 	frm.call({
		// 		method:'create_and_email_ics_file',
		// 		doc:frm.doc,
		// 	callback:function(response){
		// 		if (response.message) {
		// 			frappe.msgprint('Calendar event ics file send successfully.');
		// 	} 	else {
		// 			frappe.msgprint('Failed to send ics file.');
		// 		}
		// 	}
		// 	})
		},
		meeting_scheduled_time: function(frm) {
			if (frm.doc.repeat_this_event == 0) {
				frm.set_value("meeting_scheduled_time", "");
				frappe.throw("Please click the 'Repeat this Event' checkbox.");
				frm.refresh_field("meeting_scheduled_time");
			}
		},
		repeat_this_event:function(frm) {
			if (frm.doc.repeat_this_event == 0) {
				frm.set_value("meeting_scheduled_time", "");
				frm.refresh_field("meeting_scheduled_time");
			}
		},
	});
	