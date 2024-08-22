# Copyright (c) 2022, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, time_diff_in_hours,add_to_date


class ProjectAllocationBill(Document):
	@frappe.whitelist()
	def get_project_allo_bill(self):
		val=frappe.db.get_value("Sales Invoice",{"project_allocation_bill":self.name},["name"])
		val2=frappe.db.get_value("Sales Order",{"project_allocation_bill":self.name},["name"])
		if not val and not val2:
			return True
		
	def on_submit(self):
		self.db_set('state', "To Bill")
		self.make_sales_invoice()
		for i in self.unreconciled_items:
			pa=frappe.get_doc("Project Allocation Bill",i.project_allocation_bill)
			pa.db_set("reconciled_in_project_allocation_bill",self.name)
			pa.db_set('state', "Completed")
		alloc=frappe.db.sql("""select ra.name,rai.task ,sum(rai.allocation) as hours ,rai.project from `tabResource Allocation` ra
											join `tabResource Allocation Items` rai on rai.parent = ra.name
											where rai.project = "{0}" and 
											date(ra.date) >= "{1}" and
											date(ra.date) <="{2}" 
           									and rai.allocation is not null 
                     and (COALESCE(rai.sales_invoice,'')='' OR COALESCE(rai.sales_order,'')='') group by rai.task""".format(self.project,self.from_date,self.to_date),as_dict=1)				
		for i in alloc:
			doc=frappe.get_doc("Resource Allocation",i.get("name"))
			for i in doc.resource_allocation_items:
				if self.project==i.get("project"):
					i.project_allocation_bill=self.name
			doc.save(ignore_permissions=True)	




	def before_cancel(self):
		self.db_set('state', "Cancelled")
		b=frappe.db.get_value("Sales Invoice",{"project_allocation_bill":self.name},['name'])
		if b:
			doc=frappe.get_doc("Sales Invoice",b)
			if doc.docstatus==1:
				doc.cancel()
			else:
				doc.project_allocation_bill=""
		l=frappe.db.get_value("Sales Order",{"project_allocation_bill":self.name},['name'])
		if l:
			doc=frappe.get_doc("Sales Order",l)
			if doc.docstatus==1:
				doc.cancel()
			else:
				doc.project_allocation_bill=""
		for i in self.unreconciled_items:
			pa=frappe.get_doc("Project Allocation Bill",i.project_allocation_bill)
			pa.db_set("reconciled_in_project_allocation_bill","")
			pa.db_set('state', "To Bill")
		alloc=frappe.db.sql("""select ra.name,rai.task ,sum(rai.allocation) as hours ,rai.project from `tabResource Allocation` ra
											join `tabResource Allocation Items` rai on rai.parent = ra.name
											where rai.project = "{0}" and 
											date(ra.date) >= "{1}" and
											date(ra.date) <="{2}" 
           									and rai.allocation is not null 
                     and (COALESCE(rai.sales_invoice,'')='' OR COALESCE(rai.sales_order,'')='') group by rai.task""".format(self.project,self.from_date,self.to_date),as_dict=1)				
		for i in alloc:
			doc=frappe.get_doc("Resource Allocation",i.get("name"))
			for i in doc.resource_allocation_items:
				if self.project==i.get("project"):
					i.project_allocation_bill=""
			doc.save(ignore_permissions=True)
				

	
	@frappe.whitelist()
	def make_sales_invoice(self):
		db=frappe.db.get_value("Sales Invoice",{"project_allocation_bill":self.name},["name"])
		if db:
			frappe.throw("Sales Invoice {0} already created against project allocation bill".format(db))
		da=frappe.db.get_value("Sales Order",{"project_allocation_bill":self.name},["name"])
		if da:
			frappe.throw("Sales Order {0} already created against project allocation bill".format(db))

		time_project = frappe.db.sql(""" select name from `tabProject`
                                        where billing_based_on = 'Allocation Based' and status= "Open" and is_active="Yes" and name='{0}'
                                            """.format(self.project), as_dict=True)
       
		for proj in time_project:
			tprj = frappe.get_doc("Project", proj['name'])
			alloc=[]
			for i in self.items:
				alloc.append(i.allocation_in_hours)					
			for i in self.unreconciled_items:
				alloc.append(i.unreconciled_hrs)
			if len(alloc)>0:
				alloc=sum(alloc)
				doctype = tprj.auto_creation_doctype
				SI = frappe.new_doc(doctype)
				if doctype == "Sales Order":
					SI.naming_series = tprj.sales_order_naming_series
					SI.delivery_date = frappe.utils.nowdate()
				if doctype == "Sales Invoice":
					SI.naming_series = tprj.sales_invoice_naming_series
				
				SI.customer = tprj.customer
				SI.currency = tprj.currency
				SI.due_date = frappe.utils.nowdate()
				SI.project = tprj.name
				SI.ignore_timesheets=1
				SI.company = tprj.company
				if tprj.cost_center:
					SI.cost_center=tprj.cost_center
				else:
					company=frappe.get_doc("Company",tprj.company)
					SI.cost_center=company.cost_center
					
				SI.taxes_and_charges=tprj.sales_taxes_charges_template
				if tprj.terms:
					SI.tc_name=tprj.terms
				if tprj.price_list:
					SI.selling_price_list=tprj.price_list
				if not tprj.price_list and tprj.customer:
					doc=frappe.get_doc("Customer",tprj.customer)
					if doc.default_price_list:
						SI.selling_price_list=doc.default_price_list

				alloc_item_rate = frappe.db.get_value("Item Price",{'name':tprj.allocation_item,'price_list':SI.selling_price_list},['price_list_rate'])
					
				

				

				
				if tprj.auto_creation_doctype=="Sales Order":
					SI.project_allocation_bill=self.name
					SI.append("items", {
						"item_code": tprj.allocation_item,
						"description":"Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(self.from_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(self.to_date)+"\n (YYYY-MM-DD)",
						"qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>alloc else alloc,
						"rate": alloc_item_rate,
						"conversion_factor": 1,
					})
				des=""
				a={"1":"Jan","2":"Feb","3":"Mar","4":"Apr","5":"May","6":"Jun","7":"Jul","8":"Aug","9":"Sep","10":"Oct","11":"Nov","12":"Dec"}

				if tprj.auto_creation_doctype=="Sales Invoice" and flt(alloc)>0:
					SI.project_allocation_bill=self.name
					SI.remarks="Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(self.from_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(self.to_date)+"\n (YYYY-MM-DD)",
					if len(self.unreconciled_items)>0:
						for j in self.unreconciled_items:
							if j.idx==1:
								pa=frappe.get_doc("Project Allocation Bill",j.project_allocation_bill)
								z=[]
								for k in pa.rec_items:
									z.append(k.timesheet_hours)
								des="Implementation Services charges based on the Resource allocation billing for the period of " +"<b>"+str(self.from_date)+ "</b> to <b>" +str(self.to_date)+"</b><br>"+"Allocation for "+ str(a.get(str(getdate(self.from_date).month)))+"=<b> "+str(round(self.total,2))+" Hrs</b>"+"<br>"+"Reconciled "+ str(a.get(str(getdate(pa.from_date).month))) +"=(<b>"+str(round(pa.total,2))+"</b> Hrs "+ str(a.get(str(getdate(pa.from_date).month)))+" Allocation )-( <b>"+ str(round(sum(z),2)) +" Hrs</b> "+ str(a.get(str(getdate(pa.from_date).month))) +" Timesheet) = <b>"+str(round(j.unreconciled_hrs,2))+"</b><br><b>Net Payable "+ str(a.get(str(getdate(self.from_date).month)))+" = "+str(round(alloc,2))+" Hrs </b>"
					else:
						des="Implementation Services charges based on the Resource allocation billing for the period of " +"<b>"+str(self.from_date)+ "</b> to <b>" +str(self.to_date)+"</b><br>"+"Allocation for "+ str(a.get(str(getdate(self.from_date).month)))+"=<b> "+str(round(self.total,2))+" Hrs</b>"+"<br><b>Net Payable "+ str(a.get(str(getdate(self.from_date).month)))+" = "+str(round(alloc,2))+" Hrs </b>"

					company=frappe.get_doc("Company",tprj.company)
					SI.append("items", {
						"item_code": tprj.allocation_item,
						"qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>alloc else alloc,
						"description":des,
						"cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
						"rate": alloc_item_rate,
						"conversion_factor": 1,
					})
				if tprj.auto_creation_doctype=="Sales Invoice" and flt(alloc)<0:
					des="Implementation Services charges based on the Resource allocation billing for the period of " +"<b>"+str(self.from_date)+ "</b> to <b>" +str(self.to_date)+"</b><br>"+"Allocation for "+ str(a.get(str(getdate(self.from_date).month)))+"=<b> "+str(round(self.total,2))+" Hrs</b>"+"<br><b>Net Payable "+ str(a.get(str(getdate(self.from_date).month)))+" = "+str(round(alloc,2))+" Hrs </b>"

					SI.project_allocation_bill=self.name
					SI.remarks="Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(self.from_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(self.to_date)+"\n (YYYY-MM-DD)",
					company=frappe.get_doc("Company",tprj.company)
					SI.append("items", {
						"item_code": tprj.allocation_item,
						"qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>alloc else alloc,
						"description":des,
						"cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
						"rate": alloc_item_rate,
						"conversion_factor": 1,
					})
					SI.is_return=1
				if tprj.sales_taxes_charges_template:
					tax=frappe.get_doc("Sales Taxes and Charges Template",tprj.sales_taxes_charges_template)
					for i in tax.taxes:
						SI.append("taxes", {
							"charge_type": i.charge_type,
							"description":i.description,
							"account_head": i.account_head,
							"rate": i.rate
						})
				if tprj.terms:
					term=frappe.get_doc("Terms and Conditions",tprj.terms)
					SI.terms=term.terms
				SI.save(ignore_permissions=True)
				SI.validate()
				if tprj.auto_creation_doctype=="Sales Order":
					tprj.last_billing_date=self.to_date
				if tprj.auto_creation_doctype=="Sales Invoice":
					tprj.last_billing_date=self.to_date
				tprj.save(ignore_permissions=True)
				self.db_set('state', "To Reconcile")
				tprj.reload()
				SI.flags.ignore_validate_update_after_submit = True
				if tprj.auto_submit_invoice == 1 or tprj.auto_submit_order == 1:
					SI.validate()
					SI.submit()

				alloc = frappe.db.sql("""select name from `tabResource Allocation` 
										where date(date) >= "{0}" and
											date(date) <= "{1}" """.format(self.from_date,self.to_date),as_dict=1)
				if alloc:
					for ra in alloc:
						falloc = frappe.get_doc("Resource Allocation",ra.get("name"))
						for i in falloc.resource_allocation_items:
							if i.project==tprj.name:
								if tprj.auto_creation_doctype=="Sales Order":
									i.sales_order = SI.name
								else:
									i.sales_invoice = SI.name
								falloc.save(ignore_permissions=True)
					


			else:
				frappe.msgprint("No Resource Allocation Found So No Sales Invoice/Sales Order  is Generated. ")


	def validate(self):
		doc=frappe.db.get_all("Project Allocation Bill",{"docstatus":1,"project":self.project},["name"])
		if doc:
			for j in doc:
				pa=frappe.get_doc("Project Allocation Bill",j.name)
				if getdate(pa.from_date)<=getdate(self.from_date) <=getdate(pa.to_date) or getdate(pa.from_date)<=getdate(self.to_date) <=getdate(pa.to_date):
					frappe.throw("""Project Allocation Bill {0} Already Created For Date Range """.format(pa.name))
    

	def before_save(self):
		self.recalculate()
	@frappe.whitelist()
	def recalculate(self):
		self.unreconciled_items=[]
		self.items=[]
		m=[]
		u=[]
		alloc=frappe.db.sql("""select rai.name,rai.task ,sum(rai.allocation) as hours from `tabResource Allocation` ra
											join `tabResource Allocation Items` rai on rai.parent = ra.name
											where rai.project = "{0}" and 
											date(ra.date) >= "{1}" and
											date(ra.date) <="{2}" 
           									and rai.allocation is not null 
                     and (COALESCE(rai.sales_invoice,'')='' OR COALESCE(rai.sales_order,'')='') group by rai.task""".format(self.project,self.from_date,self.to_date),as_dict=1)				
		
		for i in alloc:
			m.append(i.get("hours"))
			self.total=sum(m)

			ta=frappe.get_doc("Task",i.get("task"))
			if ta.fixed_cost_based_billing==0:
				self.append("items",{
					"task":i.get("task"),
					"subject":ta.subject,
					"allocation_in_hours":i.get("hours")
				})
		db=frappe.db.get_all("Project Allocation Bill",{"state":"Ready To Reconcile","project":self.project,"docstatus":1},["name"])
		if db:
			for h in db:
				pa=frappe.get_doc("Project Allocation Bill",h.name)
				if not pa.reconciled_in_project_allocation_bill:
					self.append("unreconciled_items",{
						"project_allocation_bill":pa.name,
						"from_date":pa.from_date,
						"to_date":pa.to_date,
						"unreconciled_hrs":flt(pa.diff_hours)				
						})
					u.append(pa.diff_hours)
			self.reconciled_total=sum(u)

	@frappe.whitelist()
	def get_reconciled_allocation(self):
		self.rec_items=[]
		t=[]
		diff_hours=[]
		task=[]
		timesheet=frappe.db.sql("""select td.task,sum(td.billing_hours) as hours from `tabTimesheet` t join `tabTimesheet Detail` td where td.parent=t.name  and td.project = "{0}" and 
                                            (date(td.from_time) between "{1}" and '{2}' or 
                                            date(td.to_time) between "{1}" and '{2}') and t.docstatus=1 group by td.task """.format(self.project,self.from_date,self.to_date),as_dict=1)
		for i in timesheet:
			doc=frappe.get_doc("Task",i.get("task"))
			if doc.fixed_cost_based_billing==0:
			
				task.append(doc.name)
				t.append({
					"task":i.get("task"),
					"subject":doc.subject,
					"timesheet_hours":i.get("hours"),
					"allocation_in_hours": 0,
					"difference_in_hours": 0
				})
		for k in self.items:
			if k.get("task") in task:
				for j in t:
					if k.get("task")==j.get("task"):
						j.update({"allocation_in_hours":k.get("allocation_in_hours"),"difference_in_hours":flt(j.get("timesheet_hours"))-flt(k.get("allocation_in_hours"))})
						# diff_hours.append(flt(j.get("timesheet_hours"))-flt(k.get("allocation_in_hours"))) 
						
			else:
				doc=frappe.get_doc("Task",k.get("task"))
				if doc.fixed_cost_based_billing==0:
					t.append({
						"task":k.get("task"),
						"subject":doc.subject,
						"timesheet_hours":0,
						"allocation_in_hours":k.get("allocation_in_hours"),
						"difference_in_hours":-flt(k.get("allocation_in_hours"))
					})
				# diff_hours.append(flt(k.get("allocation_in_hours")))
		for i in t:
			if i.get("timesheet_hours") and not i.get("allocation_in_hours"):
				i.update({"difference_in_hours":i.get("timesheet_hours")})
				# diff_hours.append(i.get("timesheet_hours"))

		for i in t:
			diff_hours.append(i.get("difference_in_hours"))
		if	len(diff_hours) >0:
			self.timesheet_difference=sum(diff_hours)
			self.diff_hours=sum(diff_hours)
		if flt(self.diff_hours) ==0:
			self.db_set('state', "Completed")
		else:
			self.db_set('state', "Ready To Reconcile")
		return t
                

			
