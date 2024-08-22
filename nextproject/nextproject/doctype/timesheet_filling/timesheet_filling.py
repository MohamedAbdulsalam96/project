# Copyright (c) 2022, Dexciss and contributors
# For license information, please see license.txt 

from datetime import date

from erpnext.projects.doctype.timesheet.timesheet import OverlapError
import frappe
from frappe.model.document import Document
from frappe.utils.data import add_to_date, flt, get_datetime, get_time, getdate, now
import numpy as np
import datetime

class TimesheetFilling(Document):
	@frappe.whitelist()
	def fetch_allocation(self):
		self.timesheet_items=[]
		d=frappe.db.sql("""select project,name,subject,parent_task,progress,exp_end_date,duration_per_day_in_hours,actual_time,expected_time from `tabTask` where primary_consultant='{0}'and exp_start_date<='{1}'and exp_end_date >='{1}' and status not in ("Completed", "Cancelled") and is_group=0""".format(self.employee,self.date),as_dict=1)
		for i in d:
			tm=frappe.db.sql("""select t.name as tim ,ti.name as ti ,ti.description,ti.hours ,ti.from_time,ti.to_time from `tabTimesheet` t join `tabTimesheet Detail` ti on t.name=ti.parent where ti.task='{0}'  and  date(t.start_date)='{1}' and date(t.end_date)='{1}' and t.docstatus=0 and t.employee='{2}' """.format(i.name,self.date,self.employee),as_dict=1)
			if tm:
				if  i.expected_time>0:
					progress = (i.actual_time/i.expected_time) * 100 if (i.actual_time/i.expected_time) * 100 < 100 else 100
				else:
					progress=0
				pro = frappe.get_doc("Project", i.project, ["activity_type"])			
				if pro:
					activity_type = pro.activity_type

				self.append("timesheet_items",{
					"project":i.get("project"),
					"project_name": pro.project_name,
					"task":i.get("name"),
					"subject":i.get("subject"),
					"parent_task":i.get("parent_task"),
					"description":tm[0].get("description"),
					"time_spentin_hours":tm[0].get("hours"),
					"completed_before":progress,
					"from_time":tm[0].get("from_time"),
					"to_time":tm[0].get("to_time"),
					"allocationin_hours":i.get("duration_per_day_in_hours"),
					"activity_type":activity_type if pro else None,
					"expected_end_date":i.get("exp_end_date"),
					"timesheet":tm[0].get("tim"),
					"timesheet_line_id":tm[0].get("ti")
				})
			else:
				if  i.expected_time>0:
					progress = (i.actual_time/i.expected_time) * 100 if (i.actual_time/i.expected_time) * 100 < 100 else 100
				else:
					progress=0
				pro = frappe.get_doc("Project", i.project, ["activity_type"])			
				if pro:
					activity_type = pro.activity_type

				self.append("timesheet_items",{
					"project":i.get("project"),
					"project_name": pro.project_name,
					"task":i.get("name"),
					"subject":i.get("subject"),
					"parent_task":i.get("parent_task"),
					"from_time":datetime.datetime.combine(getdate(self.date), get_time(now())),
					"to_time":datetime.datetime.combine(getdate(self.date), get_time(now())),
					"completed_before":progress,
					"allocationin_hours":i.get("duration_per_day_in_hours"),
					"activity_type":activity_type if pro else None,
					"expected_end_date":i.get("exp_end_date"),
				})


		return True


	@frappe.whitelist()
	def make_timesheet(self):

		if not self.timesheet_items:
			frappe.throw("Fetch Allocation first")

		for i in self.timesheet_items:
			task=frappe.get_doc("Task",i.task)
			if task.expected_time<=0:
				frappe.throw("Row {0}: Task Expected Time Is 0".format(i.idx))
				
			if task.expected_time>0 and i.description:
				ts=frappe.get_doc("Timesheet Settings")
				for k in ts.timesheet_settings_items:
					if float(task.expected_time) in np.arange(k.from_hours,k.to_hours,0.1):
						if len(i.description)<=k.character:
							frappe.throw("Row {0} : Please Add More Description".format(i.idx))


				if not i.description:
					frappe.throw(
					frappe._("Row {0}: Description is mandatory.").format(
						i.idx
					)
					)
				if not i.time_spentin_hours:
					frappe.throw(
					frappe._("Row {0}:Time Spent In Hours is mandatory.").format(
						i.idx
					)
					)
				
		projects = []	
		for pro in self.timesheet_items:
			projects.append(pro.project)

		projects = set(projects)
		projects = list(projects)
		k=[]
		for a in projects:
			ts = frappe.get_doc("Timesheet Settings")
			pj = frappe.get_doc("Project", a)
			for i in self.timesheet_items:
				if i.timesheet:
					val=frappe.db.get_value("Timesheet",{"name":i.timesheet,"employee":self.employee},["name"])
					if val:
						ax=frappe.get_doc("Timesheet",i.timesheet)
						k.append(i.task)
						if a == i.project:
							ax.company=pj.company
							if i.description and task.expected_time:
								for kj in ax.time_logs:
									kj.task=i.task
									kj.description=i.description
									kj.from_time=i.from_time
									kj.to_time=i.to_time
									kj.hours=i.time_spentin_hours
									kj.activity_type=i.activity_type
							f = frappe.get_doc("Task", i.task)
							if f.actual_time and f.expected_time:
								if (f.actual_time / f.expected_time) * 100 < 100:
									f.progress = (f.actual_time / f.expected_time) * 100
								else:
									f.progress = 100
							exp_date = i.next_expected_end_date
							if exp_date:
								f.exp_end_date = i.next_expected_end_date
							f.save(ignore_permissions=True)
							ax.save(ignore_permissions=True)
			
		for a in projects:
			ts = frappe.get_doc("Timesheet Settings")
			pj = frappe.get_doc("Project", a)
			j = frappe.new_doc("Timesheet")
			j.employee = self.employee
			j.employee_name = self.employee_name
			j.department = self.department
			j.customer = pj.customer
			j.currency = pj.currency
			j.project = pj.name
			j.company= pj.company
			zk=0
			for i in self.timesheet_items:
				if not i.timesheet:
					if a == i.project:
						if i.description and task.expected_time:
							zk=1
							j.append(
								"time_logs",
								{
									"from_date": self.date,
									"hours": i.time_spentin_hours,
									"project": a,
									"activity_type": i.activity_type,
									"task": i.task,
									"description": i.description,
									"from_time": i.from_time,
									"to_time": i.to_time,
									"completed": 1,
								},
							)
						f = frappe.get_doc("Task", i.task)
						if f.actual_time and f.expected_time:
							if (f.actual_time / f.expected_time) * 100 < 100:
								f.progress = (f.actual_time / f.expected_time) * 100
							else:
								f.progress = 100
						exp_date = i.next_expected_end_date
						if exp_date:
							f.exp_end_date = i.next_expected_end_date
						f.save(ignore_permissions=True)
			if  zk==1:
				j.save(ignore_permissions=True)
		return True