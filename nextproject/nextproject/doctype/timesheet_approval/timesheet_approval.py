# Copyright (c) 2022, Dexciss and contributors
# For license information, please see license.txt

import json
from lib2to3.refactor import get_all_fix_names
from webbrowser import get
import frappe
from frappe.model.document import Document
import datetime
from datetime import datetime, timedelta


class TimesheetApproval(Document):
	@frappe.whitelist()
	def approved(self,timesheet_line_id,is_billable,billing_hrs):
		doc=frappe.get_doc("Timesheet Detail", timesheet_line_id)
		frappe.db.set_value("Timesheet Detail", timesheet_line_id, "approved", 1)
		frappe.db.set_value("Timesheet Detail", timesheet_line_id, "is_billable", is_billable)
		frappe.db.set_value("Timesheet Detail", timesheet_line_id, "billing_hours", billing_hrs)

		
		tk=[]
		doc1=frappe.get_doc("Timesheet", doc.parent)
		for i in doc1.time_logs:
			if i.approved!=1:
				tk.append(i.task)
		if len(tk)==0:
			doc1.approved=1
			doc1.save(ignore_permissions=1)
			doc1.submit()
		if len(tk)>0:
			doc1.save(ignore_permissions=1)



	@frappe.whitelist()
	def bulk_approved(self,items):
		for k in items:
			if k.get("__checked"):
				doc=frappe.get_doc("Timesheet Detail", k.get("timesheet_line_id"))
				frappe.db.set_value("Timesheet Detail", k.get("timesheet_line_id"), "approved", 1)
				frappe.db.set_value("Timesheet Detail", k.get("timesheet_line_id"), "is_billable", k.get("is_billable"))
				frappe.db.set_value("Timesheet Detail",  k.get("timesheet_line_id"), "billing_hours", k.get("billing_hrs"))
				tk=[]
				doc1=frappe.get_doc("Timesheet", doc.parent)
				for i in doc1.time_logs:
					if i.approved!=1:
						tk.append(i.task)
				if len(tk)==0:
					doc1.approved=1
					doc1.save(ignore_permissions=1)
					doc1.submit()
				if len(tk)>0:
					doc1.save(ignore_permissions=1)

					
	def before_save(self):
		for i in self.timesheet_details:
			doc=frappe.get_doc("Timesheet Detail", i.timesheet_line_id)
			a=doc.from_time
			print(a)
			b=doc.to_time
			print(b)
			c=b-a
			i.timesheet_duration = doc.hours* 3600
			i.remaining_time = i.expected_time - i.time_already_spent

	@frappe.whitelist()
	def get_emp(self):
		today = datetime.today()
		end_date = today - timedelta(days=7)
		self.from_date = end_date
		self.to_date = today

