# Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt

from datetime import date
from erpnext.projects.doctype.timesheet.timesheet import OverlapError
import frappe
from frappe.model.document import Document
from frappe.utils.data import add_to_date, flt, get_datetime, getdate

class TaskCompletion(Document):
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
	def fetch_task_details(self):
		self.task_new = []
		self.task_overdue = []
		self.task_pending_review = []
		self.task_open = []
		self.task_working = []
		if (self.employee_group and self.primary_consultant) or self.primary_consultant:
			task_new = frappe.get_all("Task",{'primary_consultant':self.primary_consultant,'status':'New','is_group':0})
			if task_new:
				for tn in task_new:
					self.append("task_new",{'task_id':tn.name,'subject':frappe.db.get_value('Task',tn.name,'subject'),'project_name':frappe.db.get_value('Task',tn.name,'project_name'),'start_date':frappe.db.get_value('Task',tn.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',tn.name,'exp_end_date')})
			task_pending_review = frappe.get_all("Task",{'primary_consultant':self.primary_consultant,'status':'Pending Review','is_group':0})
			if task_pending_review:
				for tpr in task_pending_review:
					self.append("task_pending_review",{'task_id':tpr.name,'subject':frappe.db.get_value('Task',tpr.name,'subject'),'project_name':frappe.db.get_value('Task',tpr.name,'project_name'),'start_date':frappe.db.get_value('Task',tpr.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',tpr.name,'exp_end_date')})
			task_overdue = frappe.get_all("Task",{'primary_consultant':self.primary_consultant,'status':'Overdue','is_group':0})
			if task_overdue:
				for to in task_overdue:
					self.append("task_overdue",{'task_id':to.name,'subject':frappe.db.get_value('Task',to.name,'subject'),'project_name':frappe.db.get_value('Task',to.name,'project_name'),'start_date':frappe.db.get_value('Task',to.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',to.name,'exp_end_date')})
			task_open = frappe.get_all("Task",{'primary_consultant':self.primary_consultant,'status':'Open','is_group':0})
			if task_open:
				for top in task_open:
					self.append("task_open",{'task_id':top.name,'subject':frappe.db.get_value('Task',top.name,'subject'),'project_name':frappe.db.get_value('Task',top.name,'project_name'),'start_date':frappe.db.get_value('Task',top.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',top.name,'exp_end_date')})
			task_working = frappe.get_all("Task",{'primary_consultant':self.primary_consultant,'status':'Working','is_group':0})
			if task_working:
				for tw in task_working:
					self.append("task_working",{'task_id':tw.name,'subject':frappe.db.get_value('Task',tw.name,'subject'),'project_name':frappe.db.get_value('Task',tw.name,'project_name'),'start_date':frappe.db.get_value('Task',tw.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',tw.name,'exp_end_date')})
			if not self.task_overdue and not self.task_pending_review and not self.task_open and not self.task_working:
				frappe.msgprint("Task Is Not Allocated")
		else:
			if self.employee_group:
				team_members = frappe.get_all("Employee Group Table",{'parent':self.employee_group},['employee'])
				for emp in team_members:
					task_new = frappe.get_all("Task",{'primary_consultant':self.primary_consultant,'status':'New','is_group':0})
					if task_new:
						for tn in task_new:
							self.append("task_new",{'task_id':tn.name,'subject':frappe.db.get_value('Task',tn.name,'subject'),'project_name':frappe.db.get_value('Task',tn.name,'project_name'),'start_date':frappe.db.get_value('Task',tn.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',tn.name,'exp_end_date')})
					task_pending_review = frappe.get_all("Task",{'primary_consultant':emp.employee,'status':'Pending Review','is_group':0})
					if task_pending_review:
						for tpr in task_pending_review:
							self.append("task_pending_review",{'task_id':tpr.name,'subject':frappe.db.get_value('Task',tpr.name,'subject'),'project_name':frappe.db.get_value('Task',tpr.name,'project_name'),'start_date':frappe.db.get_value('Task',tpr.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',tpr.name,'exp_end_date')})
					task_overdue = frappe.get_all("Task",{'primary_consultant':emp.employee,'status':'Overdue','is_group':0})
					if task_overdue:
						for to in task_overdue:
							self.append("task_overdue",{'task_id':to.name,'subject':frappe.db.get_value('Task',to.name,'subject'),'project_name':frappe.db.get_value('Task',to.name,'project_name'),'start_date':frappe.db.get_value('Task',to.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',to.name,'exp_end_date')})
					task_open = frappe.get_all("Task",{'primary_consultant':emp.employee,'status':'Open','is_group':0})
					if task_open:
						for top in task_open:
							self.append("task_open",{'task_id':top.name,'subject':frappe.db.get_value('Task',top.name,'subject'),'project_name':frappe.db.get_value('Task',top.name,'project_name'),'start_date':frappe.db.get_value('Task',top.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',top.name,'exp_end_date')})
					task_working = frappe.get_all("Task",{'primary_consultant':emp.employee,'status':'Working','is_group':0})
					if task_working:
						for tw in task_working:
							self.append("task_working",{'task_id':tw.name,'subject':frappe.db.get_value('Task',tw.name,'subject'),'project_name':frappe.db.get_value('Task',tw.name,'project_name'),'start_date':frappe.db.get_value('Task',tw.name,'exp_start_date'),'end_date':frappe.db.get_value('Task',tw.name,'exp_end_date')})
				if not self.task_overdue and not self.task_pending_review and not self.task_open and not self.task_working:
					frappe.msgprint("Task Is Not Allocated.")
		return True

@frappe.whitelist()
def new_to_open(doc_id):
    if doc_id:
        get_task_id = frappe.get_doc("Task", doc_id)
        get_task_id.status = 'Open'
        get_task_id.save(ignore_permissions=True)
        frappe.msgprint("Task Status Changed to Open")
    return True

@frappe.whitelist()
def pending_review_to_complete(doc_id):
	if doc_id:
		get_task_id = frappe.get_doc("Task",doc_id)
		get_task_id.status = 'Completed'
		get_task_id.completed_by = frappe.db.get_value("Employee",get_task_id.primary_consultant,'user_id')
		get_task_id.completed_on = date.today()
		get_task_id.save(ignore_permissions=True)
		frappe.msgprint("Task Status Changed to Completed Successfully")
	return True

@frappe.whitelist()
def overdue_to_working(doc_id):
	if doc_id:
		get_task_id = frappe.get_doc("Task",doc_id)
		get_task_id.status = 'Working'
		get_task_id.save(ignore_permissions=True)
		frappe.msgprint("Task Status Changed to Working Successfully")
	return True

@frappe.whitelist()
def open_to_working(doc_id):
	if doc_id:
		get_task_id = frappe.get_doc("Task",doc_id)
		get_task_id.status = 'Working'
		get_task_id.save(ignore_permissions=True)
		frappe.msgprint("Task Status Changed to Working Successfully")
	return True

@frappe.whitelist()
def working_to_preview(doc_id): 
	if doc_id:
		get_task_id = frappe.get_doc("Task",doc_id)
		get_task_id.status = 'Pending Review'
		get_task_id.save(ignore_permissions=True)
		frappe.msgprint("Task Status Changed to Pending Review Successfully")
	return True
