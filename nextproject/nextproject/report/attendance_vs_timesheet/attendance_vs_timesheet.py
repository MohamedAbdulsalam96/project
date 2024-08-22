4# Copyright (c) 2022, Dexciss and contributors
# For license information, please see license

from calendar import monthrange
import calendar

import frappe
import pandas as pd
from frappe import _, msgprint
from datetime import datetime
from datetime import date
from frappe.utils import cint, cstr, getdate
from frappe.utils import getdate,add_to_date,time_diff_in_hours

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(data,filters)
	return columns, data , None , chart

def get_columns(filters):
	col =	[
				{
					"fieldname":"employee",
					"label": ("Employee"),
					"fieldtype": "Link",
					"options" : "Employee"
				},
				{
					'label': 'Employee Name',
					'fieldname': 'employee_name',
					'fieldtype': 'Data',
					
				},
				
				
					
		]

	year = int(filters.year)
	month = int(filters.month)
	mm = filters.month if len(filters.month) == 2 else "0"+filters.month 
	
	num_days = calendar.monthrange(year, month)[1]
	for day in range(1,num_days+1):
		dd = day if len(str(day)) == 2 else "0"+ str(day)
		date = str(filters.year) + "-" + str(mm)+ "-" + str(dd)
		print("New",date)

	# days = [datetime.date(str(year), str(month), day) for day in range(1, num_days+1)]
	
		
	
		
		date_col = {
			'label': date+" "+"(Attendance)",
			'fieldname': date+"_"+"att",
			'fieldtype': 'Data',
			
		}
		working_col = {
			'label': date+" "+"(Working)",
			'fieldname': date+"_"+"wh",
			'fieldtype': 'Data',
			
		}
		billable_col = {
			'label': date+" "+"(Billable)",
			'fieldname': date+"_"+"bw",
			'fieldtype': 'Data',
			
		}
		col.append(date_col)
		col.append(working_col)
		col.append(billable_col)
	# print("col is: ",default_col)
	return col
	

def get_data(filters):
	# dynamic = {}
	eps = []
	dates_l = []
	year = int(filters.year)
	month = int(filters.month)
	mm = filters.month if len(filters.month) == 2 else "0"+filters.month 
	
	num_days = calendar.monthrange(year, month)[1]
	for day in range(1,num_days+1):
		dd = day if len(str(day)) == 2 else "0"+ str(day)
		date = str(filters.year) + "-" + str(mm)+ "-" + str(dd)
		print("New",date)
		dates_l.append(date)

	
	
	if filters.get("employee"):
		emp_filters = {'status':"Active",'name':filters.get("employee")}
	else:
		emp_filters = {'status':"Active"}

	emp = frappe.db.get_all("Employee",emp_filters,["name","employee_name"])
	if emp:
		for i in emp:
			dynamic = {
				"employee":i.name,
				"employee_name":i.employee_name
			}

			for dt in dates_l:
				
				att_filters = {'employee':i.name,'attendance_date':dt,'docstatus':1}
				
				att = frappe.db.get_all("Attendance",att_filters,["employee","status","shift"])
				
				
				
				if att:
					for wh in att:
						
						if wh.employee == i.name:
							if wh.status == "Present" :
								# color = fg('green')
								atd = "P"
								

								if wh.shift :
									shift = frappe.get_doc("Shift Type",wh.shift)
									diff= time_diff_in_hours(shift.end_time ,shift.start_time)
									whs = diff
								else:
									whs = dshift.standard_working_hours
							elif wh.status == "Absent":
								atd =  "A"
								# atd_c = Fore.RED + atd
								whs = 0.0
							elif wh.status == "On Leave":
								atd = "L"
								whs = 0.0
							elif wh.status == "Half Day":
								atd = "HD"
								if wh.shift :
									shift = frappe.get_doc("Shift Type",wh.shift)
									diff= time_diff_in_hours(shift.end_time ,shift.start_time)
									whs = float(diff/2)
								else:
									dshift = frappe.get_doc("HR Settings")
									whs = (dshift.standard_working_hours/2)


							elif wh.status == "Work From Home":
								atd = "WFH"
								if wh.shift :
									shift = frappe.get_doc("Shift Type",wh.shift)
									diff= time_diff_in_hours(shift.end_time ,shift.start_time)
									whs = float(diff/2)
								else:
									dshift = frappe.get_doc("HR Settings")
									whs = dshift.standard_working_hours

							
							whc = dt+ "_" + "wh"
							atdn = dt+ "_"+ "att"

							dynamic.update({
								whc:whs,
								atdn:atd
							})
				
				else:
					dshift = frappe.get_doc("HR Settings")
					whc = dt+ "_"+ "wh"
					atdn = dt +"_"+ "att"
					atd = "UA"

					whs = dshift.standard_working_hours
					dynamic.update({
								whc:whs,
								atdn:atd

							})

				billable=frappe.db.sql(""" select sum(ti.billing_hours) as hours , t.employee as emp from `tabTimesheet` t 
											join `tabTimesheet Detail` ti
										on ti.parent=t.name where date(from_time)="{0}"and t.employee="{1}"  and t.docstatus = 1""".format(dt,i.name),as_dict = 1)
				if billable:
					for k in billable:
						if k.emp == i.name:
							billh = dt+ "_" + 'bw'
							bw = k.hours
							

							dynamic.update({
								billh:bw 
							})



			

			eps.append(dynamic)

							

		return eps

def get_chart_data(data,filters):
	print("data",data)
	sep = "_"
	
	d_list = []
	b_list = []
	all_dts = []
	billable = ""
	actual = ""
	allocation = ""
	wh = ""

	year = int(filters.year)
	month = int(filters.month)
	mm = filters.month if len(filters.month) == 2 else "0"+filters.month 
	
	num_days = calendar.monthrange(year, month)[1]
	for day in range(1,num_days+1):
		dd = day if len(str(day)) == 2 else "0"+ str(day)
		date = str(filters.year) + "-" + str(mm)+ "-" + str(dd)
		print("New",date)
		all_dts.append(date)
	

	
	

	value3 = []
	value4 = []
	value = []
	value2 = []
	labels = []

	for q in all_dts:
		sum_alloc = 0.0
		sum_billable = 0.0
		sum_actual = 0.0
		sum_wh = 0.0
		labels.append(q)
		billable = q +"_" + "bw"
		
		wh = q +"_"+ "wh"
		




		if data:
			for i in data:
				
				print("keys!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",i.keys())
				
				sum_billable += i.get(billable) if i.get(billable) else 0
			
				
			
				sum_wh += i.get(wh) if i.get(wh) else 0

			value.append(sum_billable)
			
			value4.append(sum_wh)

		print("chardt data",labels,value)
		print("b_list",b_list)
		
		datasets1 = []
		if value:
			datasets1.append({'name': ('Billable Hours'), 'values': value})
		
		if value4:
			datasets1.append({'name': ('Working Hours'), 'values': value4})
		
		
		
		

		chart1 = {
			"data": {
				'labels': labels,
				'datasets': datasets1
			},
		}
		chart1["type"] = "bar"

		print("*********************",labels,datasets1)
	
	return chart1
		


	
	
	



