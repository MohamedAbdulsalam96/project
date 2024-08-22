# Copyright (c) 2022, Dexciss and contributors
# For license information, please see license.txt



import frappe
import datetime
from frappe.model.document import Document
from datetime import date, timedelta, datetime
from frappe.utils import add_to_date,getdate,time_diff_in_hours
from datetime import date

from frappe.utils.data import flt, nowdate, today

class ResourceAllocation(Document):
	def validate(self):
		alloc = 0.0
		if self.resource_allocation_items:
			for i in self.resource_allocation_items:
				alloc += i.allocation
		self.allocation = alloc
		if float(self.working_hours) > 0:
			self.rup = (self.allocation/float(self.working_hours))*100
			if self.rup > 100:
				self.rup = 100
		else:
			self.rup = 0.0

		
	def before_save(self):
		hour=[]
		for i in self.resource_allocation_items:
			hour.append(i.allocation)
		if len(hour)>0:
			self.allocation=sum(hour)
		else:
			self.allocation=0


@frappe.whitelist()
def create_resource_allocation(values):
	frappe.enqueue(
		method=get_task, queue="long",timeout=1000,
		is_async=True, values=values
	)
	frappe.msgprint("Method In Queues in background Job It takes Maximum 10 Min to Complete Allocation")

	
@frappe.whitelist()
def get_task(values):
	values=eval(values)
	ra_filters = {}
	tk_filters = {}


	if values.get("exp_start_date") and values.get("exp_end_date"):

		sd = values.get("exp_start_date")
		ed = values.get("exp_end_date")
		now = getdate(sd)
		now1= getdate(ed)
		dlist = []

		Days =  (now1 -now).days + 1
		for i in range(Days):
			ob = frappe.utils.add_days(now, i)
			dlist.append(ob)
		res=dlist

	if values.get("primary_consultant"):
		ra_filters.update({
			"primary_consultance":values.get("primary_consultant")
		})
		tk_filters.update({
			"primary_consultant":values.get("primary_consultant")
		})

	if values.get("project_lead"):
		ra_filters.update({
			"project_lead":values.get("project_lead")
		})
		tk_filters.update({
			"project_lead":values.get("project_lead")
		})
	if values.get("task"):
		ra_filters.update({
			"task":values.get("task")
		})
		tk_filters.update({
			"name":values.get("task")
		})
	if values.get("project"):
		ra_filters.update({
			"project":values.get("project")
		})
		tk_filters.update({
			"project":values.get("project")
		})

	if values.get("exp_start_date") and values.get("exp_end_date"):
		tk_filters.update({
			"exp_start_date":["in", (values.get("exp_start_date"),values.get("exp_end_date"))]
		})
		tk_filters.update({
			"exp_end_date":["in", (values.get("exp_start_date"),values.get("exp_end_date"))]
		})
	
	
	conditions = ""
	
	if values.get("task"):
		conditions += "and tk.name = '{0}' ".format(values.get("task"))
	if values.get("project"):
		conditions+= "and tk.project = '{0}'".format(values.get("project"))
	filt_emp = values.get("primary_consultant") if values.get("primary_consultant") else ""

	if values.get("primary_consultant"):
		fen= frappe.db.get_all("Employee",{"name":values.get("primary_consultant")},["name","employee_name"])
	else:
		fen = frappe.db.get_all("Employee",{"status":"Active"},['*'])
	for name in fen:
		emp_holi = frappe.db.get_value("Employee",{"name":name.get("name")},["holiday_list"])
		if values.get("project"):
			proj=frappe.db.get_value("Project",{"name":values.get("project")},["holiday_list"])
			if proj:
				phdlist = frappe.db.get_all("Holiday",{"parent":proj},["holiday_date"])
				if phdlist:
					for ph in phdlist:
						if ph.get("holiday_date") in dlist:
							dlist.remove(ph.get("holiday_date"))
							res = [i for i in dlist if i not in phdlist]
						else:
							res=dlist
		elif emp_holi:
			hdlist = frappe.db.get_all("Holiday",{"parent":emp_holi},["holiday_date"])
			if hdlist:
				for dt in hdlist:
					if dt.get("holiday_date") in dlist:
						dlist.remove(dt.get("holiday_date"))
						res = [i for i in dlist if i not in hdlist]
					else:
						res=dlist
			else:
				hlist = frappe.db.get_all("Holiday",{"parent":emp_holi},["holiday_date"])
				for dt in hlist:
					if dt.get("holiday_date") in dlist:
						dlist.remove(dt.get("holiday_date"))
						res = [i for i in dlist if i not in hlist]
					else:
						res=dlist
			
			
		elif not emp_holi:
			emp_holi = frappe.db.get_value("Employee",{"name":name.get("name")},["default_shift"])
			if emp_holi:
				shift=frappe.db.get_value("Shift Type",{"name":emp_holi},["holiday_list"])
				if shift:
					hdlist = frappe.db.get_all("Holiday",{"parent":emp_holi},["holiday_date"])
					if hdlist:
						for dt in hdlist:
							if dt.get("holiday_date") in dlist:
								dlist.remove(dt.get("holiday_date"))
								res = [i for i in dlist if i not in hdlist]
							else:
								res=dlist
					else:
						hlist = frappe.db.get_all("Holiday",{"parent":emp_holi},["holiday_date"])
						for dt in hlist:
							if dt.get("holiday_date") in dlist:
								dlist.remove(dt.get("holiday_date"))
								res = [i for i in dlist if i not in hlist]
							else:
								res=dlist

		else:
			res=dlist

		for dt in res:
			abc = ("""
					select 
					ep.name as id, 
					ep.employee_name as name , 
					ep.reports_to as rpt,
					"{1}" as date, 
					sum(tk.duration_per_day_in_hours) as alloc, 
					tk.name as tid,
					tk.project as pro_id,
					tk.project_lead_name as prol_name,
					tk.project_lead as prol_id,
					tk.subject as sub,
					tk.progress as prog,
					
					
					
					
					case 
					when att.employee = "{0}" and att.status = "Present" and att.shift IS NOT NULL then
					(select st.actual_working_hours_without_break from `tabShift Type` as st where st.name = att.shift)
					
					when att.status = "Absent" then
					(select 0.0)
					
					
					when att.status = "Work From Home" and att.shift IS NOT NULL then
					(select st.actual_working_hours_without_break from `tabShift Type` as st where st.name = att.shift)
					
		
					when att.employee = "{0}" and att.status = "Present" and att.shift IS NULL then
					if((select st.actual_working_hours_without_break
						from  `tabShift Assignment` sa 
						left outer join `tabShift Type` st on st.name = sa.shift_type
						where 
						sa.docstatus = 1 and 
						sa.employee = "{0}" and 
						sa.status = "Active"  and 
						case when sa.start_date IS  not null and sa.end_date IS not null
						then
						sa.start_date <= "{1}" and sa.end_date >= "{1}"
						else
						sa.start_date <= "{1}" and sa.end_date is NULL

						end
						limit 1),
					(select st.actual_working_hours_without_break as hd 
						from  `tabShift Assignment` sa 
						left outer join `tabShift Type` st on st.name = sa.shift_type
						where 
						sa.docstatus = 1 and 
						sa.employee = "{0}" and 
						sa.status = "Active"  and 
						case when sa.start_date IS  not null and sa.end_date IS not null
						then
						sa.start_date <= "{1}" and sa.end_date >= "{1}"
						else
						sa.start_date <= "{1}" and sa.end_date is NULL

						end
						limit 1),
					(if((select st.actual_working_hours_without_break from `tabShift Type` as st where st.name = ep.default_shift),
					(select st.actual_working_hours_without_break from `tabShift Type` as st where st.name = ep.default_shift),
					((select value from `tabSingles`  
						where doctype = "HR Settings" and field = "standard_working_hours")))))
					
					
					
					
					
					when att.status = "Work From Home" and att.shift IS NULL then
					if((select st.actual_working_hours_without_break
						from  `tabShift Assignment` sa 
						left outer join `tabShift Type` st on st.name = sa.shift_type
						where 
						sa.docstatus = 1 and 
						sa.employee = "{0}" and 
						sa.status = "Active"  and 
						case when sa.start_date IS  not null and sa.end_date IS not null
						then
						sa.start_date <= "{1}" and sa.end_date >= "{1}"
						else
						sa.start_date <= "{1}" and sa.end_date is NULL

						end
						limit 1),
					(select st.actual_working_hours_without_break
						from  `tabShift Assignment` sa 
						left outer join `tabShift Type` st on st.name = sa.shift_type
						where 
						sa.docstatus = 1 and 
						sa.employee = "{0}" and 
						sa.status = "Active"  and 
						case when sa.start_date IS  not null and sa.end_date IS not null
						then
						sa.start_date <= "{1}" and sa.end_date >= "{1}"
						else
						sa.start_date <= "{1}" and sa.end_date is NULL

						end
						limit 1),
					(if((select st.actual_working_hours_without_break from `tabShift Type` as st where st.name = ep.default_shift),
					(select st.actual_working_hours_without_break from `tabShift Type` as st where st.name = ep.default_shift),
					((select value from `tabSingles`  
						where doctype = "HR Settings" and field = "standard_working_hours")))))
					
					
					
					
					when att.status = "Half Day" and att.shift IS NOT NULL then
					(select (st.actual_working_hours_without_break/2) from `tabShift Type` as st where st.name = att.shift)
					
		
					when att.status = "Half Day" and att.shift IS NULL then
					if( (select (st.actual_working_hours_without_break/2)
						from  `tabShift Assignment` sa 
						left outer join `tabShift Type` st on st.name = sa.shift_type
						where 
						sa.docstatus = 1 and 
						sa.employee = "{0}" and 
						sa.status = "Active"  and 
						case when sa.start_date IS  not null and sa.end_date IS not null
						then
						sa.start_date <= "{1}" and sa.end_date >= "{1}"
						else
						sa.start_date <= "{1}" and sa.end_date is NULL

						end
						limit 1),
					(select (st.actual_working_hours_without_break/2)
						from  `tabShift Assignment` sa 
						left outer join `tabShift Type` st on st.name = sa.shift_type
						where 
						sa.docstatus = 1 and 
						sa.employee = "{0}" and 
						sa.status = "Active"  and 
						case when sa.start_date IS  not null and sa.end_date IS not null
						then
						sa.start_date <= "{1}" and sa.end_date >= "{1}"
						else
						sa.start_date <= "{1}" and sa.end_date is NULL

						end
						limit 1),
					(if((select (st.actual_working_hours_without_break/2) from `tabShift Type` as st where st.name = ep.default_shift),
					(select (st.actual_working_hours_without_break/2) from `tabShift Type` as st where st.name = ep.default_shift),
					((select value/2 from `tabSingles`  
						where doctype = "HR Settings" and field = "standard_working_hours")))))
					
					
					
					
				when att.status = "On Leave" then
					(select 0.0)
					
					
					else 
					(if((select st.actual_working_hours_without_break
						from  `tabShift Assignment` sa 
						left outer join `tabShift Type` st on st.name = sa.shift_type
						where 
						sa.docstatus = 1 and 
						sa.employee = "{0}" and 
						sa.status = "Active"  and 
						case when sa.start_date IS  not null and sa.end_date IS not null
						then
						sa.start_date <= "{1}" and sa.end_date >= "{1}"
						else
						sa.start_date <= "{1}" and sa.end_date is NULL

						end
						limit 1),
					(select st.actual_working_hours_without_break
						from  `tabShift Assignment` sa 
						left outer join `tabShift Type` st on st.name = sa.shift_type
						where 
						sa.docstatus = 1 and 
						sa.employee = "{0}" and 
						sa.status = "Active"  and 
						case when sa.start_date IS  not null and sa.end_date IS not null
						then
						sa.start_date <= "{1}" and sa.end_date >= "{1}"
						else
						sa.start_date <= "{1}" and sa.end_date is NULL

						end
						limit 1),
					(if((select st.actual_working_hours_without_break from `tabShift Type` as st where st.name = ep.default_shift),
					(select st.actual_working_hours_without_break from `tabShift Type` as st where st.name = ep.default_shift),
					((select value from `tabSingles`  
						where doctype = "HR Settings" and field = "standard_working_hours"))))))

					end  as wh
					
					


					


					from 
					`tabEmployee` as ep
					left outer join  `tabTask` as tk on ep.name = tk.primary_consultant and tk.exp_start_date <= "{1}" and tk.exp_end_date >= "{1}" and tk.is_group = 0 and tk.is_template = 0 and tk.status not in ("Template","Completed","Cancelled")

					left outer join `tabAttendance` as att on att.employee = "{0}" and att.attendance_date = "{1}" and att.docstatus = 1
				
					
					
					
					where  ep.status = "Active" and
					ep.name = "{0}"
					{3}
				

					
					
					group by tk.primary_consultant , tk.name
					""".format(filt_emp if filt_emp != "" else name.get("name"),dt,name.get("employee_name"),conditions))

	
			query = frappe.db.sql(abc,as_dict=1)
			
			for i in query:
				if i.get("pro_id"):
					project=frappe.get_doc("Project",i.get("pro_id"))
					
					if project.is_active=="Yes" and project.status=="Open":
						ra_check = frappe.db.get_value("Resource Allocation",{'primary_consultance':i.get("id"),'date':i.get("date")},['name'])
						if ra_check:
							doc=frappe.get_doc("Resource Allocation",ra_check)
							a=[]
							for d in doc.resource_allocation_items:
								a.append(d.task)
							for j in doc.resource_allocation_items:
								if j.project==i.get("pro_id") and j.task==i.get("tid"):
									j.update({
											"project":i.get("pro_id"),
											"task":i.get("tid"),
											"allocation":i.get("alloc"),
											"project_lead":i.get("prol_id"),
											"project_lead_name":i.get("prol_name"),
											"task_subject":i.get("sub"),
											"task_progress":i.get("prog")
										})
								
							if i.get("tid") not in a:
								doc.append("resource_allocation_items",{
									"project":i.get("pro_id"),
									"task":i.get("tid"),
									"allocation":i.get("alloc"),
									"project_lead":i.get("prol_id"),
									"project_lead_name":i.get("prol_name"),
									"task_subject":i.get("sub"),
									"task_progress":i.get("prog")
								})
							doc.save()
							frappe.msgprint("Resource Allocation Created For Date - {0} and Employee - {1}".format(doc.date,doc.primary_consultance))
							doc.reload()

						if not ra_check:
							ra = frappe.new_doc("Resource Allocation")
							ra.primary_consultance = i.get("id")
							ra.primary_consultant_name = i.get('name')
							ra.reports_to = i.get("rpt")
							ra.project_lead_name = i.get("prol_name")
							ra.date = i.get("date")
							ra.working_hours = i.get("wh")

							if i.get("alloc") and i.get("pro_id") and i.get("tid"):
								ra.append("resource_allocation_items",{
									"project":i.get("pro_id"),
									"task":i.get("tid"),
									"allocation":i.get("alloc"),
									"project_lead":i.get("prol_id"),
									"project_lead_name":i.get("prol_name"),
									"task_subject":i.get("sub"),
									"task_progress":i.get("prog")
								})

							ra.save()
							frappe.msgprint("Resource Allocation Created For Date - {0} and Employee - {1}".format(ra.date,ra.primary_consultance))
							ra.reload()

						ra_check = frappe.db.get_value("Resource Allocation",{'primary_consultance':i.get("id"),'date':i.get("date")},['name'])
						if ra_check:
							doc=frappe.get_doc("Resource Allocation",ra_check)
							for ik in doc.resource_allocation_items:
								doc=frappe.get_doc("Task",ik.task)
								if doc.status=="Cancelled":
									frappe.delete_doc("Resource Allocation Items", ik.name)
							doc.save(ignore_permissions=True)



				
					
						
@frappe.whitelist()
def split(name,values,date,hours,a,task,pc):
	doc=frappe.get_doc("Resource Allocation",name)
	if getdate(eval(values).get("date"))<=getdate(date):
		frappe.throw("Not Allowed To Dated Before {0}".format(date))
	if (eval(values).get("hours")) >float(hours):
		frappe.throw("Not Allowed To More Than {0}".format(hours))
	value=frappe.db.get_value("Resource Allocation",{"date":eval(values).get("date"),"primary_consultance":pc},["name"])
	if not value:
		frappe.throw("Allocation Not Found date {0} for Employee {1}".format(eval(values).get("date"),pc))
	if (eval(values).get("hours"))>0 and value:
		for i in doc.resource_allocation_items:
			if a==i.name:
				i.allocation=i.allocation-(eval(values).get("hours"))
				doc.allocation=doc.allocation-i.allocation
		doc.save(ignore_permissions=True)
		
		if value:
			new_doc=frappe.get_doc("Resource Allocation",value)
			task1=[]
			proj=[]
			for j in new_doc.resource_allocation_items:
				task1.append(j.task)
				proj.append(j.project)
			for j in new_doc.resource_allocation_items:
				
				if j.task==task:
					j.allocation=flt(j.allocation)+flt((eval(values).get("hours")))
					new_doc.allocation=new_doc.allocation+j.allocation
					task1.remove(task)
			if task in task1:
				child=frappe.get_doc("Resource Allocation Items",a)
				new_doc.append("resource_allocation_items",{"allocation":eval(values).get("hours"),
								"task":task,"project":child.project,"project_lead_name":child.project_lead_name})
				new_doc.allocation=new_doc.allocation+j.allocation

			new_doc.save(ignore_permissions=True)
			if len(new_doc.resource_allocation_items)==0:
				child=frappe.get_doc("Resource Allocation Items",a)
				new_doc.append("resource_allocation_items",{"allocation":eval(values).get("hours"),
								"task":task,"project":child.project,"project_lead_name":child.project_lead_name})
				new_doc.allocation=eval(values).get("hours")
			new_doc.save(ignore_permissions=True)
			frappe.msgprint("Allocation Shifted {0} Date ".format(new_doc.date))
			return True
	

	
@frappe.whitelist()					
def move(name,values,date,hours,a,task,pc):
	doc=frappe.get_doc("Resource Allocation",name)
	
	if getdate(eval(values).get("date"))<=getdate(date):
		frappe.throw("Not Allowed To Dated Before {0}".format(date))
	
	if (eval(values).get("hours")) >float(hours):
		frappe.throw("Not Allowed To More Than {0}".format(hours))
	value=frappe.db.get_value("Resource Allocation",{"date":eval(values).get("date"),"primary_consultance":pc},["name"])
	if not value:
		frappe.throw("Allocation Not Found date {0} for Employee {1}".format(eval(values).get("date"),pc))	
	if (eval(values).get("hours"))>0 and value:
		for i in doc.resource_allocation_items:
			if a==i.name:
				i.allocation=i.allocation-(eval(values).get("hours"))
				doc.allocation=doc.allocation-i.allocation
		doc.save(ignore_permissions=True)
	if value:
		new_doc=frappe.get_doc("Resource Allocation",value)
		task2=[]
		for j in new_doc.resource_allocation_items:
			task2.append(j.task)
		
		for j in new_doc.resource_allocation_items:
			if j.task==task:
				j.allocation=flt(j.allocation)+flt((eval(values).get("hours")))
				new_doc.allocation=new_doc.allocation+j.allocation
				task2.remove(task)
		if task in task2:
			child=frappe.get_doc("Resource Allocation Items",a)
			new_doc.append("resource_allocation_items",{"allocation":eval(values).get("hours"),
							"task":task,"project":child.project,"project_lead_name":child.project_lead_name})
			new_doc.allocation=new_doc.allocation+j.allocation

		new_doc.save(ignore_permissions=True)
		if len(new_doc.resource_allocation_items)==0:
			child=frappe.get_doc("Resource Allocation Items",a)
			new_doc.append("resource_allocation_items",{"allocation":eval(values).get("hours"),
							"task":task,"project":child.project,"project_lead_name":child.project_lead_name})
			new_doc.allocation=eval(values).get("hours")
		new_doc.save(ignore_permissions=True)

		frappe.msgprint("Allocation Shifted {0} Date ".format(new_doc.date))

		return True

			
			
			
			
			

						


		