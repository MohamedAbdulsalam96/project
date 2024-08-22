# Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.reportview import get_match_cond
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
from frappe.utils.data import getdate, today
from datetime import datetime

class DailyScrum(Document):

	@frappe.whitelist()
	def task_details(self,task):
		task=frappe.get_doc("Task",task)
		z=[]
		if len(task.checklist_items)>0:
			
			for i in task.checklist_items:
				z.append({"particulars":i.particulars,"expected_end_date":i.expected_end_date,"completed":i.completed,"completion_date":i.completion_date,"hours":i.hours})

			return task.description,z
		return task.description,z

	@frappe.whitelist()
	def team_filters(self):
		if self.team:
			employee_list=[]
			team_members=frappe.get_doc("Employee Group",{"name":self.team})
			for team in team_members.employee_list:
				employee_list.append(team.employee)
			
			return employee_list
				
		
	@frappe.whitelist()
	def update_task(self,values,task):
		task=frappe.get_doc("Task",task)
		value=values
		task.checklist_items=[]
		if value.get("checklist_items"):
			task.append("checklist_items",{
				"particulars":value.get("checklist_items")[0].get("particulars"),
				"expected_end_date":value.get("checklist_items")[0].get("expected_end_date"),
				"completed":value.get("checklist_items")[0].get("completed"),
				"completion_date":value.get("checklist_items")[0].get("completion_date"),
				"hours":value.get("checklist_items")[0].get("hours")
			})
			task.save(ignore_permissions=True)

	@frappe.whitelist()
	def morning_data(self):
		if self.type == "Morning" and self.team:
			if self.docstatus == 0:
				team_members = self.team_mebers
				emp_team = frappe.get_doc("Employee Group", self.team)
				existing_members = {item.member for item in self.team_scrum}

				new_team_members = {team.employee for team in emp_team.employee_list if any(emp.employee == team.employee for emp in team_members)}
				self.team_scrum = [item for item in self.team_scrum if item.member in new_team_members]

				existing_members = {item.member for item in self.team_scrum}

				for team in emp_team.employee_list:
					for emp in team_members:
						if team.employee == emp.employee and team.employee not in existing_members:
							task_doc = frappe.db.get_values("Task", {
								"primary_consultant": team.employee,
								"status": ["not in", ["Completed", "Cancelled", "Hold"]],
								"employee_group": self.team,
								"is_group": 0,
								"exp_start_date": ['<=', self.date]
							}, ["name", "subject", "status", "exp_end_date", "exp_start_date", "project_name", "expected_time", "actual_time", "custom_progress_status", "employee_group"], as_dict=1)

							if task_doc:
								for j in task_doc:
									self.append("team_scrum", {
										"member": team.employee,
										"member_name": team.employee_name,
										"current_task": j.get("name"),
										"subject": j.get("subject"),
										"project": j.get("project_name"),
										"status": j.get("status"),
										"old_status": j.get("status"),
										"expected_end_date": j.get("exp_end_date"),
										"expected_start_date": j.get("exp_start_date"),
										"expected_time": j.get("expected_time"),
										"time_spent": j.get("actual_time"),
										"progress_status": j.get("custom_progress_status")
									})
							else:
								self.append("team_scrum", {
									"member": team.employee,
									"member_name": team.employee_name
								})


	def validate(self):
		existing_scrums = frappe.db.get_all(
			"Daily Scrum",
			filters={"team": self.team, "date": self.date},
			fields=["name", "type"]
		)
		for exist in existing_scrums:
			if exist['name'] != self.name and exist['type'] == self.type:
				exist_doc = frappe.get_doc("Daily Scrum", exist['name'])
				for member in exist_doc.team_mebers:
					for team in self.team_mebers:
						if member.employee==team.employee:
							frappe.throw("Already, one of the team member {0} has presented the scrum attendance.".format(member.employee))


	@frappe.whitelist()
	def state_change(self,task,status):
		if task:
			tas=frappe.get_doc("Task",task)
			tas.status=status
			if status=="Completed":
				tas.completed_by=frappe.session.user
				tas.completed_on=getdate(today())
			tas.save(ignore_permissions=True)
		

	@frappe.whitelist()
	def evening_data(self):
		if self.type == "Evening":
			eve=frappe.get_doc("Daily Scrum",self.morning_scrum)
			self.follow_up_scrum_items = []
			self.lead=eve.lead
			self.lead_name=eve.lead_name
			for emp in eve.team_scrum:
				# time_sheet=frappe.get_doc("Timesheet",{""})
				time_sheet = frappe.db.sql("""
										SELECT t.name,t.employee
										FROM `tabTimesheet` AS t
										JOIN `tabTimesheet Detail` AS td ON td.parent = t.name
										WHERE t.employee='{0}' and  
										'{1}' between date(td.from_time) and date(td.to_time) and t.docstatus in (0,1) and company='{2}' and task='{3}'
									""".format(emp.member,self.date,self.company,emp.current_task), as_dict=True)
				status=frappe.db.get_value("Task",{"name":emp.current_task},"status")
				if status!="Completed":
					
					if time_sheet:
						self.append("follow_up_scrum_items", {
									"member": emp.member,
									"merber_name": emp.member_name,
									"current_task": emp.current_task,
									"subject":emp.subject,
									"project_name":emp.project,
									"status": emp.status,
									"old_status":emp.status,
									"expected_end_date": emp.expected_end_date,
									"on_track": emp.on_track,
									"expected_start_date":emp.expected_start_date,
									"notes":emp.notes,
									"progress_status":emp.progress_status,
									"timesheet": time_sheet[0].get("name") if emp.member == time_sheet[0].get("employee") else "",
									"ignore_timesheet_check":emp.ignore_timesheet_check
								})

					else:
						self.append("follow_up_scrum_items",{
							"member":emp.member,
							"merber_name":emp.member_name,
							"current_task":emp.current_task,
							"subject":emp.subject,
							"project_name":emp.project,
							"status":emp.status,
							"old_status":emp.status,
							"expected_end_date":emp.expected_end_date,
							"expected_start_date":emp.expected_start_date,
							"on_track":emp.on_track,
							"notes":emp.notes,
							"progress_status":emp.progress_status,
							"timesheet":"",
							"ignore_timesheet_check":emp.ignore_timesheet_check
						})
	@frappe.whitelist()
	def evening_team_filters(self):
		if self.type == "Evening":
			morning_members=[]
			mor=frappe.get_doc("Daily Scrum",self.morning_scrum)
			for team in mor.team_mebers:
				morning_members.append(team.employee)
			return morning_members
			
	
	def before_submit(self):
		team_members = [value.employee for value in self.team_mebers]
		for emp in team_members:
			doc = frappe.new_doc("Scrum Attendance")
			doc.employee = emp
			doc.type = "Scrum Attendee"
			user_pid = frappe.get_value("Employee", {"employee":emp}, "prefered_email")
			doc.user=user_pid
			doc.attendance = "Present"
			doc.status = "Present"
			doc.attendance_date = self.date
			doc.daily_scrum= self.name
			doc.insert(ignore_permissions=True)
			doc.submit()
			
		if self.lead:
			t_doc = frappe.new_doc("Scrum Attendance")
			t_doc.employee = self.lead
			t_doc.type = "Scrum Master"
			user_leadid = frappe.get_value("Employee", {"employee":self.lead}, "prefered_email")
			t_doc.user=user_leadid
			t_doc.attendance = "Present"
			t_doc.status = "Present"
			t_doc.attendance_date = self.date
			t_doc.daily_scrum=self.name
			t_doc.insert(ignore_permissions=True)
			t_doc.submit()
			
		if self.team:
			team_doc = frappe.get_doc("Employee Group", {"name": self.team})
			all_employee = [team.employee for team in team_doc.employee_list]

			for ab in all_employee:
				if ab not in team_members:
					ab_doc = frappe.new_doc("Scrum Attendance")
					ab_doc.employee = ab
					ab_doc.type = "Scrum Attendee"
					user_id = frappe.get_value("Employee", {"employee": ab}, "prefered_email")
					ab_doc.user = user_id
					ab_doc.attendance = "Absent"
					ab_doc.status= "Absent"
					ab_doc.attendance_date = self.date
					ab_doc.daily_scrum=self.name
					ab_doc.insert(ignore_permissions=True)
					ab_doc.submit()
			
		for task in self.team_scrum:
			task_doc = frappe.get_doc("Task", task.current_task)
			comm="""<div class="ql-editor read-mode"><pre class="ql-code-block-container" spellcheck="false"><div class="ql-code-block">"""
			comm+="Date: "+str(self.get_formatted("date"))+"<br>"+str(self.type)+" Scrum | "+str(self.team)
			comm+="</div></pre></div>"
			if task.old_status !=task.status or task_doc.employee_group != task.change_team or task_doc.exp_end_date!=task.new_end_date:
				if task.new_end_date or task.old_status !=task.status or task.change_team: 
					comm+="<br><b>Action Taken: </b>"
			if task.old_status !=task.status:
				comm +="Status Changed | "
			if task.change_team:
				if task_doc.employee_group != task.change_team:
					comm+="Team Changed | "
			if task.new_end_date:
				if task_doc.exp_end_date!=task.expected_end_date:
					comm+="End Date Changed"
			if task.old_status !=task.status or task_doc.employee_group != task.change_team or task_doc.exp_end_date!=task.new_end_date:
				if task.new_end_date or task.old_status !=task.status or task.change_team: 
					comm+="<br><b>Updated Value: </b>"
			if task.old_status !=task.status:
				comm +=str(task.old_status)+"->"+str(task.status)+" | "
			if task.change_team:
				if task_doc.employee_group != task.change_team:
					comm +=str(task_doc.employee_group)+"->"+str(task.change_team)+" | "
			if task_doc.exp_end_date!=task.new_end_date:
				if task.new_end_date:
					comm+=str(task_doc.get_formatted("exp_end_date"))+"->"+str(task.get_formatted("new_end_date"))
			comm+="<br><b>Notes: </b> "+str(task.notes)
			emp=frappe.get_doc("Employee",self.lead)
			task_doc.add_comment('Comment', text=comm,comment_email=emp.user_id)

			if task.new_end_date:
				task_doc.exp_end_date = task.new_end_date
			if task.update_start_date:
				task_doc.exp_start_date = task.update_start_date
			task_doc.custom_progress_status=task.progress_status
			if task_doc.employee_group!=task.change_team:
				if task.change_team:
					em=frappe.get_doc("Employee Group",task.change_team)
					task_doc.employee_group=task.change_team
					task_doc.primary_consultant=em.group_lead
				task_doc.flags.ignore_validate = True
				task_doc.save(ignore_permissions=True)
		for task in self.follow_up_scrum_items:
			task_doc = frappe.get_doc("Task", task.current_task)
			comm="""<div class="ql-editor read-mode"><pre class="ql-code-block-container" spellcheck="false"><div class="ql-code-block">"""
			comm+="Date: "+str(self.get_formatted("date"))+"<br>"+str(self.type)+" Scrum | "+str(self.team)
			comm+="</div></pre></div>"
			if task.old_status !=task.status  or task_doc.exp_end_date!=task.new_end_date:
				if task.new_end_date or task.old_status !=task.status: 
					comm+="<br><b>Action Taken: </b>"
			if task.old_status !=task.status:
				comm +="Status Changed | "
			if task.new_end_date:
				if task_doc.exp_end_date!=task.new_end_date:
					comm+="End Date Changed"
			if task.old_status !=task.status  or task_doc.exp_end_date!=task.new_end_date:
				if task.new_end_date or task.old_status !=task.status:
					comm+="<br><b>Updated Value: </b> "
			if task.old_status !=task.status:
				comm +=str(task.old_status)+"->"+str(task.status)+" | "
			if task_doc.exp_end_date!=task.new_end_date:
				if task.new_end_date:
					comm+=str(task_doc.get_formatted("exp_end_date"))+"->"+str(task.get_formatted("new_end_date"))
			comm+="<br><b>Notes: </b> "+str(task.evening_notes)
			emp=frappe.get_doc("Employee",self.lead)
			task_doc.add_comment('Comment', text=comm,comment_email=emp.user_id)
			task_doc = frappe.get_doc("Task", task.current_task)
			if task.new_end_date:
				task_doc.exp_end_date = task.new_end_date
			if task.update_start_date:
				task_doc.exp_start_date = task.update_start_date

			task_doc.custom_progress_status=task.progress_status
			task_doc.flags.ignore_validate = True
			task_doc.save(ignore_permissions=True)
		for j in self.team_scrum:
			if not j.notes or j.on_track==0 and not j.new_end_date:
				frappe.throw("Row {0}: Notes and New Delivery Date Mandatory".format(j.idx))

		for k in self.follow_up_scrum_items:
			if not k.ignore_timesheet_check:
				if not k.evening_notes or k.on_track==0 and not k.new_end_date or not k.timesheet:
						frappe.throw("Row {0}: Notes , New Delivery Date and Timesheet Is Mandatory".format(k.idx))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def task_query(doctype, txt, searchfield, start, page_len, filters):
	doctype = "Timesheet"
	condition = ""
	meta = frappe.get_meta(doctype)
	for fieldname, value in filters.items():
		if meta.get_field(fieldname) or fieldname in frappe.db.DEFAULT_COLUMNS:
			condition += f" and {fieldname}={frappe.db.escape(value)}"

	searchfields = meta.get_search_fields()

	if searchfield and (meta.get_field(searchfield) or searchfield in frappe.db.DEFAULT_COLUMNS):
		searchfields.append(searchfield)

	search_condition = ""
	for field in searchfields:
		if search_condition == "":
			search_condition += f"`tabTimesheet`.`{field}` like '{0}'".format("%" + txt + "%")
		else:
			search_condition += f" or `tabTimesheet`.`{field}` '{0}'".format("%" + txt + "%")
	return frappe.db.sql(
		"""select
			`tabTimesheet`.name
		from
			`tabTimesheet`
		join `tabTimesheet Detail`
			on (`tabTimesheet Detail`.parent = `tabTimesheet`.name and `tabTimesheet Detail`.parenttype = 'Timesheet')
		where
			`tabTimesheet Detail`.task ='{0}' and `tabTimesheet`.employee='{1}' and `tabTimesheet`.start_date='{2}' 
			
			""".format(filters.pop("task"),filters.pop("employee"),filters.pop("from_date"),mcond=get_match_cond(doctype),
			search_condition=search_condition,
			condition=condition or "",))
		
