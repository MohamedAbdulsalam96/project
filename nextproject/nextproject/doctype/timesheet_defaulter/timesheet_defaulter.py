# Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TimesheetDefaulter(Document):
	def before_save(self):
		if self.is_new():
			ts=frappe.get_doc("Timesheet Settings")
			email_template = frappe.get_doc("Email Template",ts.email_template)
			args={}
			company_email=None
			if self.employee:
				parent_doc = frappe.get_doc("Employee", self.employee) 
				company_email=parent_doc.company_email
				args = parent_doc.as_dict()
			args.update(self.as_dict())

			if self.timesheet:
				tdoc=frappe.get_doc("Timesheet",self.timesheet)
				args.update(tdoc.as_dict())

			message = frappe.render_template(email_template.response, args)
			if self.timesheet:
				email_args = {
								"recipients": company_email,
								"subject": "Timesheet - name {0} ".format(self.timesheet),
								"message":message,
								"reference_name":self.timesheet,
							}

				frappe.enqueue(
						method=frappe.sendmail,
						queue="short",
						timeout=300,
						event=None,
						is_async=True,
						job_name=None,
						now=False,
						**email_args,
					)
			else:
				if self.name and ts.email_template:
					email_args = {
						"recipients": company_email,
						"subject": "No timesheets are available or Timesheet fill less than minimum Timesheet Hour {1} for {0}".format( self.date_for_which_hours_are_less,ts.min_timesheet_hours ),
						"message":message
					}
					frappe.enqueue(
							method=frappe.sendmail,
							queue="short",
							timeout=300,
							event=None,
							is_async=True,
							job_name=None,
							now=False,
							**email_args,
						)

