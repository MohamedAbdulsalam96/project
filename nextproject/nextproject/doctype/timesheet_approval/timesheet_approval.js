// // Copyright (c) 2022, Dexciss and contributors
// // For license information, please see license.txt

frappe.ui.form.on("Timesheet Approval",{
	fetch_timesheets: function (frm) {
		frm.clear_table("timesheet_details");
		frappe.call({
		  method: "nextproject.api.fetch_timesheet",
		  type: "POST",
		  args: {
			employee: frm.doc.select_employee,
			from_date: frm.doc.from_date,
			to_date: frm.doc.to_date,
			project: frm.doc.project
		  },
		  callback: function (resp) {
			if (resp.message) {
			$.each(resp.message, function(i, r) {
			//   resp.message.map(r => {
				let row = frm.add_child("timesheet_details");
				row.project = r.project;
				row.task = r.task;
				row.subject=r.subject;
				row.activity_type = r.activity_type;
				row.date = r.from_time;
				row.actual_time = r.consume_time + r.hours;
				row.timesheet_line_id = r.name;
				row.billing_hrs = r.billing_hours;
				row.billing_rate = r.billing_rate;
				row.billing_amount = r.billing_amount;
				row.is_billable = r.is_billable;
				row.timesheet_hrs = r.hours;
				row.time_justification = r.description;
				row.timesheet = r.parent;
				row.expected_time = r.expected_time;
				row.time_already_spent = r.actual_time;
				row.remaining_time = r.remaining_time;
				row.progress = r.progress;
				// row.remaining_time =
				// console.log("dalily**************** ",r.total_duration_in_days)

				// getExpectedTimeAndProgressForEmployee(frm.doc.select_employee, function (expected_time, progress, duration_per_day_in_hours, actual_time) {
				// 	row.expected_time = expected_time;
				// 	row.progress = progress;
				// 	row.time_already_spent = actual_time;
				// 	// console.log("time_already_spent", actual_time);
				// 	row.remaining_time = duration_per_day_in_hours;
				// 	// console.log("test", duration_per_day_in_hours);
				// 	frm.refresh_field("timesheet_details");
				// });				
			  });
			  frm.refresh_fields("timesheet_details");
			}
		}
	});
	
},
refresh:function(frm){
	cur_frm.get_field('timesheet_details').grid.toggle_display("billing_hrs",false);
	cur_frm.get_field('timesheet_details').grid.toggle_display("billing_rate",false);
	cur_frm.get_field('timesheet_details').grid.toggle_display("billing_amount",false);
	frm.set_value('from_date', frappe.datetime.add_months(frappe.datetime.get_today(), -1));
	frm.set_value('to_date', frappe.datetime.get_today());

	frm.disable_save()
	
},
show_billing_info: function (frm,cdt,cdn) {
	if (frm.doc.show_billing_info == 1){
		cur_frm.get_field('timesheet_details').grid.toggle_display("billing_hrs",true);
		cur_frm.get_field('timesheet_details').grid.toggle_display("billing_rate",true);
		cur_frm.get_field('timesheet_details').grid.toggle_display("billing_amount",true);
		frm.fields_dict['timesheet_details'].grid.refresh();
	}
	else{
		cur_frm.get_field('timesheet_details').grid.toggle_display("billing_hrs");
		cur_frm.get_field('timesheet_details').grid.toggle_display("billing_rate");
		cur_frm.get_field('timesheet_details').grid.toggle_display("billing_amount");
		frm.fields_dict['timesheet_details'].grid.refresh();

	}
	}
})
frappe.ui.form.on('Timesheet Line Details', {
	
	approve:function(frm,cdt,cdn){
		let child=locals[cdt][cdn]
	frappe.call({
		method:"approved",
		doc:frm.doc,
		args:{
			"timesheet_line_id":child.timesheet_line_id,
			"is_billable":child.is_billable,
			"billing_hrs":child.billing_hrs
		},
		callback: function(response){
			frappe.msgprint("Timesheet has been successfully updated")
		}

	})
}
})
function getExpectedTimeAndProgressForEmployee(employee, callback) {
	frappe.call({
	  method: "frappe.client.get_value",
	  args: {
		doctype: "Task",
		filters: { primary_consultant: employee },
		fieldname: ["expected_time", "progress","duration_per_day_in_hours","actual_time"]
	  },
	  callback: function (response) {
		if (response && response.message) {
		  const { expected_time, progress,duration_per_day_in_hours,actual_time } = response.message;
		  callback(expected_time, progress,duration_per_day_in_hours,actual_time);
		//   console.log("=====total",response.message)
		} else {
		  callback(0, 0, 0);
		}
	  }
	});
}

frappe.ui.form.on('Timesheet Approval', {
    refresh: function(frm) {
      frm.add_custom_button(('Approve'), function(){
		var data = {items: frm.doc.timesheet_details};
		frappe.call({
			method:"bulk_approved",
			doc:frm.doc,
			args:data,
			callback: function(response){
				frappe.msgprint("Timesheet has been successfully updated")
			}
	
		})
    }).addClass('btn-primary')

  }
});
