// Copyright (c) 2022, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Timesheet Filling', {
	refresh: function(frm){
		// frm.set_value('date', frappe.datetime.get_today());

		frm.add_custom_button(__('Fetch Allocation'),function(){
			
			frappe.call({
			method:"fetch_allocation",
			doc: frm.doc,
			callback:function(r){
				if (r.message){
					frm.refresh_fields("timesheet_items")
					frm.refresh()
				}
			}
		})
	})
	
frm.set_df_property('timesheet_items', 'cannot_add_rows', 1);
frm.disable_save();
},


setup: function(frm) {
	frm.set_value('date', frappe.datetime.get_today());


	frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name', (r) => {
		frm.set_value("employee",r.name)
		frm.refresh_field("employee")
	})
	frm.add_fetch('employee', 'employee_name', 'employee_name');


	frm.fields_dict.employee.get_query = function() {
		return {
			filters:{
				'status': 'Active'
			}
		};
	};
},

submit_timesheet: function(frm) {

	frm.call({
		method: 'make_timesheet',
		doc: frm.doc,
		freeze: true,           
        freeze_message: __("Timesheet Creating"),
		callback: function(r) {
			if(r.message){
			frappe.msgprint("Timesheet Created")
			}
		}
	});
},


});
frappe.ui.form.on("Timesheet Items", {
	from_time: function(frm, cdt, cdn) {
		calculate_end_time(frm, cdt, cdn);
	},
	time_spentin_hours: function(frm, cdt, cdn) {
		calculate_end_time(frm, cdt, cdn);
	},
	to_time: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
	
		if(frm._setting_hours) return;
	
		var hours = moment(child.to_time).diff(moment(child.from_time), "seconds") / 3600;
		frappe.model.set_value(cdt, cdn, "time_spentin_hours", hours);
	}
});
var calculate_end_time = function(frm, cdt, cdn) {
	let child = locals[cdt][cdn];

	if(!child.from_time) {
		// if from_time value is not available then set the current datetime
		frappe.model.set_value(cdt, cdn, "from_time", frappe.datetime.get_datetime_as_string());
	}

	let d = moment(child.from_time);
	if(child.time_spentin_hours) {
		d.add(child.time_spentin_hours, "hours");
		frm._setting_hours = true;
		frappe.model.set_value(cdt, cdn, "to_time",
			d.format(frappe.defaultDatetimeFormat)).then(() => {
			frm._setting_hours = false;
		});
	}
};


