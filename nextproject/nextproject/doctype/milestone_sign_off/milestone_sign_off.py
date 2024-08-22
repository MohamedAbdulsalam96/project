# Copyright (c) 2021, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MilestoneSignOff(Document):
	@frappe.whitelist()
	def milestone_list(self):
		if len(self.milestone_depends_on_task)==0:
			doc=frappe.db.get_all("Task",{"project":self.project,"is_milestone":1},["name","subject"])
			for i in doc:
				self.append("milestone_depends_on_task",{
						"task":i.name,
						"subject":i.subject
					})
			return True


	def on_submit(self):
		frappe.db.set_value("Milestone Sign Off", self.name, "status1", "To Be Signed")
		self.reload()

	def on_update_after_submit(self):
		a=0
		b=0
		for i in self.milestone_depends_on_task:
			a=a+1
			if i.signature:
				b=b+1
		if a==b:
			frappe.db.set_value("Milestone Sign Off", self.name, "status1", "Fully Signed")
			self.reload()
		if a!=b:
			frappe.db.set_value("Milestone Sign Off", self.name, "status1", "Partially Signed")
			self.reload()

		for j in self.milestone_depends_on_task:
			doc=frappe.get_doc("Task",j.task)
			if j.signature:
				if doc.status=="Completed":
					pass
				else:
					frappe.throw("At Row '{0}' Milestone '{1}' Not Completed Please Complete First".format(j.idx,j.task))
		
	def validate(self):
		proj=frappe.db.get_all("Milestone Sign Off",{"docstatus":1},["project"])
		for j in proj:
			if self.project==j.project:
				frappe.throw(frappe._("Project '{0}' Must Have Only One Milestone Sign Off").format(j.project))