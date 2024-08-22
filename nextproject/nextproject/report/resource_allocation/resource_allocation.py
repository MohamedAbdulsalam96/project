# # Copyright (c) 2022, Dexciss and contributors
# # For license information, please see license.txt

import frappe
from frappe.utils import getdate,add_to_date,time_diff_in_hours
from frappe.utils.data import date_diff
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from erpnext.accounts.report.supplier_ledger_summary.supplier_ledger_summary import execute as sle_execute



def execute(filters=None):
	validate_filters(filters)
	columns, data = get_columns(filters), get_data(filters)
	chart = get_chart_data(data,filters,filters.get("periodicity"))
	report_summary = get_summary( filters ,data)
	return columns, data , None , chart , report_summary

def validate_filters(filters):
	from_date, to_date = filters.get("from_date"), filters.get("to_date")
	

	if not from_date and to_date:
		frappe.throw("From and To Dates are required.")
	elif date_diff(to_date, from_date) < 0:
		frappe.throw("To Date cannot be before From Date.")

import datetime

def get_weeks(year):
    weeks = []
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    delta = datetime.timedelta(days=7)

    current_date = start_date
    while current_date <= end_date:
        week_number = current_date.strftime("%U")
        weeks.append(week_number)
        current_date += delta

    return weeks

year = 2023 
all_weeks = get_weeks(year)
print(all_weeks)

def get_month_num():
	months = ["01-01","02-01","03-01","04-01","05-01","06-01","07-01","08-01","09-01","10-01","11-01","12-01"]
	return months

def get_months():
	months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
	return months

def get_years(filters):
	years = [filters.get("start_year")]
	if filters.get("start_year") and filters.get("end_year"):
		diff = int(filters.get("end_year")) - int(filters.get("start_year"))
		
		if diff:
			for i in range(diff):
				if str(int(filters.get("start_year")) + i) not in years:
					years.append(
						str(int(filters.get("start_year")) + i)
					)
			years.append(filters.get("end_year"))
	
	return years

def get_columns(filters):
	columns = []
	d_list=[]
	if filters.get("from_date") and filters.get("to_date"):
		sd = filters.get('from_date')
		ed = filters.get('to_date')
		d_list.append(sd)
		d_list.append(ed)

		
		dtst = [d.date() for d in pd.to_datetime(d_list)]
		stdt=dtst[0]
		edt=dtst[1]

		date_d = (edt - stdt).days + 1
		all_dts=[]
		for i in range(date_d):
			all_dts.append(add_to_date(stdt,days=i,as_string=True))
	
		employee = {
		"label": "Employee",
		"fieldname": ("employee"),
		"fieldtype": "Link",
		"options":"Employee",
		"width": 200}
		columns.append(employee)
		
		employee_name = {
		"label": "Employee Name",
		"fieldname": ("employee_name"),
		"fieldtype": "Data",
		"width": 200}
		columns.append(employee_name)

		department = {
		"label": "Department",
		"fieldname": ("department"),
		"fieldtype": "Link",
		"options":"Department",
		"width": 200}
		columns.append(department)

		designation = {
		"label": "Designation",
		"fieldname": ("designation"),
		"fieldtype": "Link",
		"options":"Designation",
		"width": 200}
		columns.append(designation)

		reports_to_name = {
		"label": "Reports To (Name)",
		"fieldname": ("reports_to_name"),
		"fieldtype": "Data",
		"width": 200}
		columns.append(reports_to_name)

		if filters.get("periodicity") == "Daily":
			for dts in all_dts:
				att_column = {
					"fieldname": str(dts)+"_"+'att',
					"label": str(dts) +" "+"(Attendance)",
					"fieldtype": "Data"

				},
				wh_column={
					"fieldname": str(dts)+"_"+'wh',
					"label": str(dts) +" "+"(Working Hours)",
					"fieldtype": "Float"
				}
				columns.append(wh_column)
				alloc_column={
					"fieldname": str(dts)+"_"+ 'alloc',
					"label": str(dts) + " "+ "(Allocation)",
					"fieldtype": "Float"
				}
				columns.append(alloc_column)
				aw_column={
					"fieldname": str(dts)+"_" + 'aw',
					"label": str(dts) + " "+"(Timesheet Hours)",
					"fieldtype": "Float"
				}
				columns.append(aw_column)
				bw_column={
					"fieldname": str(dts)+ "_" + 'bw',
					"label": str(dts) +" "+ "(Billable Hours)",
					"fieldtype": "Float"
				}
				columns.append(bw_column)
				rup_column={
					"fieldname": str(dts)+"_" + 'rup',
					"label": str(dts) + " "+"(Resource Utilization %)",
					"fieldtype": "Percent"

				}
				columns.append(rup_column)

		elif filters.get("periodicity") == "Weekly":
			week_date_ranges = []
			current_date = datetime.datetime.strptime(filters.get("from_date"), "%Y-%m-%d")

			while current_date <= datetime.datetime.strptime(filters.get("to_date"), "%Y-%m-%d"):
				print("current_date", current_date)
				to_date = current_date + datetime.timedelta(days=6)
				week_date_ranges.append({
					"from_date": current_date.strftime("%Y-%m-%d"),
					"to_date": to_date.strftime("%Y-%m-%d")
				})
				current_date += datetime.timedelta(weeks=1)

			for week in week_date_ranges:
				w_att_column = {
					"fieldname": str(week.get("from_date"))+"-"+str(week.get("to_date")) + "_att",
					"label": str(week.get("from_date"))+"-"+str(week.get("to_date")) + " " + "(Attendance)",
					"fieldtype": "Data"
				}
				columns.append(w_att_column)

				wh_column={
					"fieldname": str(week.get("from_date"))+"-"+str(week.get("to_date"))+"_"+'wh',
					"label": str(week.get("from_date"))+"-"+str(week.get("to_date")) +" "+"(Working Hours)",
					"fieldtype": "Float"
				}
				columns.append(wh_column)
				alloc_column={
					"fieldname": str(week.get("from_date"))+"-"+str(week.get("to_date"))+"_"+ 'alloc',
					"label": str(week.get("from_date"))+"-"+str(week.get("to_date")) + " "+ "(Allocation)",
					"fieldtype": "Float"
				}
				columns.append(alloc_column)
				aw_column={
					"fieldname": str(week.get("from_date"))+"-"+str(week.get("to_date"))+"_" + 'aw',
					"label": str(week.get("from_date"))+"-"+str(week.get("to_date")) + " "+"(Timesheet Hours)",
					"fieldtype": "Float"
				}
				columns.append(aw_column)
				bw_column={
					"fieldname": str(week.get("from_date"))+"-"+str(week.get("to_date"))+ "_" + 'bw',
					"label": str(week.get("from_date"))+"-"+str(week.get("to_date")) +" "+ "(Billable Hours)",
					"fieldtype": "Float"
				}
				columns.append(bw_column)
				rup_column={
					"fieldname": str(week.get("from_date"))+"-"+str(week.get("to_date"))+"_" + 'rup',
					"label": str(week.get("from_date"))+"-"+str(week.get("to_date")) + " "+"(Resource Utilization %)",
					"fieldtype": "Percent"

				}
				columns.append(rup_column)

		elif filters.get("periodicity") == "Monthly":
			month_date_ranges = []
			start_date_str = filters.get("from_date")
			end_date_str = filters.get("to_date")

			start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
			end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

			# Create a while loop to iterate through the months
			current_date = start_date
			while current_date <= end_date:
				month_start = current_date.replace(day=1)
				if current_date.month == 12:
					next_month = current_date.replace(year=current_date.year + 1, month=1)
				else:
					next_month = current_date.replace(month=current_date.month + 1)
				month_end = (next_month - timedelta(days=1))
				
				month_date_ranges.append({
					"from_date": month_start.strftime("%Y-%m-%d"),
					"to_date": month_end.strftime("%Y-%m-%d")
				})
				
				current_date = next_month

			for month in month_date_ranges:
				import calendar
				mon=getdate(month.get("from_date")).month
				year=getdate(month.get("from_date")).year
				if 1 <= mon <= 12:
					m=calendar.month_name[mon]
					w_att_column = {
						"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date")) + "_att",
						"label": str(m) +str(year)+" " + "(Attendance)",
						"fieldtype": "Data"
					}
					columns.append(w_att_column)

					wh_column={
						"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_"+'wh',
						"label": str(m) +str(year)+" "+"(Working Hours)",
						"fieldtype": "Float"
					}
					columns.append(wh_column)
					alloc_column={
						"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_"+ 'alloc',
						"label": str(m) + str(year)+" "+ "(Allocation)",
						"fieldtype": "Float"
					}
					columns.append(alloc_column)
					aw_column={
						"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_" + 'aw',
						"label": str(m) + str(year)+" "+"(Timesheet Hours)",
						"fieldtype": "Float"
					}
					columns.append(aw_column)
					bw_column={
						"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+ "_" + 'bw',
						"label": str(m) + str(year)+" "+ "(Billable Hours)",
						"fieldtype": "Float"
					}
					columns.append(bw_column)
					rup_column={
						"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_" + 'rup',
						"label": str(m) + str(year)+" "+"(Resource Utilization %)",
						"fieldtype": "Percent"

					}
					columns.append(rup_column)	
		elif filters.get("periodicity") == "Fortnightly":
			month_date_ranges = []
			interval = timedelta(days=14)

			# Initialize a list to store the date ranges
			start_date=getdate(filters.get("from_date"))
			end_date=getdate(filters.get("to_date"))
			# Start from the first date and keep adding the interval until you reach the end date
			while start_date <= end_date:
				# Calculate the end date for the current range
				end_of_fortnight = start_date + interval - timedelta(days=1)
				
				# Ensure the end date does not exceed the end_date
				if end_of_fortnight > end_date:
					end_of_fortnight = end_date
				
				# Add the current date range to the list
				month_date_ranges.append({
					"from_date": start_date.strftime("%Y-%m-%d"),
					"to_date": end_of_fortnight.strftime("%Y-%m-%d")
				})
				
				# Move to the next fortnight
				start_date = end_of_fortnight + timedelta(days=1)

			for month in month_date_ranges:
				w_att_column = {
					"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date")) + "_att",
					"label": str(month.get("from_date"))+"-"+str(month.get("to_date")) + " " + "(Attendance)",
					"fieldtype": "Data"
				}
				columns.append(w_att_column)

				wh_column={
					"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_"+'wh',
					"label": str(month.get("from_date"))+"-"+str(month.get("to_date")) +" "+"(Working Hours)",
					"fieldtype": "Float"
				}
				columns.append(wh_column)
				alloc_column={
					"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_"+ 'alloc',
					"label": str(month.get("from_date"))+"-"+str(month.get("to_date")) + " "+ "(Allocation)",
					"fieldtype": "Float"
				}
				columns.append(alloc_column)
				aw_column={
					"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_" + 'aw',
					"label": str(month.get("from_date"))+"-"+str(month.get("to_date")) + " "+"(Timesheet Hours)",
					"fieldtype": "Float"
				}
				columns.append(aw_column)
				bw_column={
					"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+ "_" + 'bw',
					"label": str(month.get("from_date"))+"-"+str(month.get("to_date")) +" "+ "(Billable Hours)",
					"fieldtype": "Float"
				}
				columns.append(bw_column)
				rup_column={
					"fieldname": str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_" + 'rup',
					"label": str(month.get("from_date"))+"-"+str(month.get("to_date")) + " "+"(Resource Utilization %)",
					"fieldtype": "Percent"

				}
				columns.append(rup_column)	


		elif filters.get("periodicity") == "Yearly":
			year_date_ranges = []
			from_date= getdate(filters.get("from_date"))
			to_date= getdate(filters.get("to_date"))

			# from_date = datetime.datetime.strptime(from_date_str, "%d-%m-%Y")
			# to_date = datetime.datetime.strptime(to_date_str, "%d-%m-%Y")


			while from_date.year <= to_date.year:
				start_date = from_date.replace(month=1, day=1)
				end_date = from_date.replace(month=12, day=31)
				
				if from_date.year == to_date.year:
					end_date = to_date
				
				year_date_ranges.append({"from_date": start_date.strftime("%d-%m-%Y"), "to_date": end_date.strftime("%d-%m-%Y")})
				
				from_date = from_date.replace(year=from_date.year + 1)

			columns = []
			for year in year_date_ranges:

				w_att_column = {
					"fieldname": str(year.get("from_date"))+"-"+str(year.get("to_date")) + "_att",
					"label": str(year.get("from_date"))+"-"+str(year.get("to_date")) + " " + "(Attendance)",
					"fieldtype": "Data"
				}
				columns.append(w_att_column)

				wh_column={
					"fieldname": str(year.get("from_date"))+"-"+str(year.get("to_date"))+"_"+'wh',
					"label": str(year.get("from_date"))+"-"+str(year.get("to_date")) +" "+"(Working Hours)",
					"fieldtype": "Float"
				}
				columns.append(wh_column)
				alloc_column={
					"fieldname": str(year.get("from_date"))+"-"+str(year.get("to_date"))+"_"+ 'alloc',
					"label": str(year.get("from_date"))+"-"+str(year.get("to_date")) + " "+ "(Allocation)",
					"fieldtype": "Float"
				}
				columns.append(alloc_column)
				aw_column={
					"fieldname": str(year.get("from_date"))+"-"+str(year.get("to_date"))+"_" + 'aw',
					"label": str(year.get("from_date"))+"-"+str(year.get("to_date")) + " "+"(Timesheet Hours)",
					"fieldtype": "Float"
				}
				columns.append(aw_column)
				bw_column={
					"fieldname": str(year.get("from_date"))+"-"+str(year.get("to_date"))+ "_" + 'bw',
					"label": str(year.get("from_date"))+"-"+str(year.get("to_date")) +" "+ "(Billable Hours)",
					"fieldtype": "Float"
				}
				columns.append(bw_column)
				rup_column={
					"fieldname": str(year.get("from_date"))+"-"+str(year.get("to_date"))+"_" + 'rup',
					"label": str(year.get("from_date"))+"-"+str(year.get("to_date")) + " "+"(Resource Utilization %)",
					"fieldtype": "Percent"

				}
				columns.append(rup_column)	


	months = get_months()
	years = get_years(filters)	

	return	columns


def get_data(filters):
	atd = ""
	whs = 0.0
	alc = 0.0
	aw = 0.0
	eps = []
	d_list = []
	all_dts = []
	if filters.get("from_date") and filters.get("to_date"):
		sd = filters.get('from_date')
		ed=filters.get('to_date')
		d_list.append(sd)
		d_list.append(ed)

		
		dtst = [d.date() for d in pd.to_datetime(d_list)]
		stdt=dtst[0]
		edt=dtst[1]
		date_d = (edt - stdt).days + 1
		for i in range(date_d):
			all_dts.append(add_to_date(stdt,days=i,as_string = True))

	if filters.get("employee"):
		emp_filters = {'status':"Active",'name':filters.get("employee")}
		
	else:
		emp_filters = {'status':"Active"}
	if filters.get("designation"):
		emp_filters.update({"designation":filters.get("designation")})
	if filters.get("department"):
		emp_filters.update({"department":filters.get("department")})
	if filters.get("reports_to_name"):
		emp_filters.update({"reports_to":filters.get("reports_to_name")})

	emp = frappe.db.get_all("Employee",emp_filters,["name","employee_name","department","designation","reports_to","holiday_list","company"])
	if emp:
		
		for i in emp:
			com=frappe.get_doc("Company",i.company)
			holiday=[]
			if i.holiday_list:
				val=frappe.get_doc("Holiday List",com.default_holiday_list)
				for k in val.holidays:
					holiday.append(getdate(k.holiday_date))

			if i.reports_to:
				rte = frappe.db.get_value("Employee",{"name":i.reports_to},["employee_name"])
			else:
				rte = ""

			dynamic = {
				"employee":i.name,
				"employee_name":i.employee_name,
				"department":i.department,
				"designation":i.designation,
				"reports_to_name":rte

			}
			if filters.get("periodicity") == "Daily":
				for dt in all_dts:
					if getdate(dt) not in holiday:
						att_filters = {'employee':i.name,'attendance_date':dt,'docstatus':1}
						alloc_filters = {'date':dt,'primary_consultance':i.name}
						
						att = frappe.db.get_all("Attendance",att_filters,["employee","status","shift"])
						print('dgfhggkhvhjkjnkvchcjvcjvjv',att)
						
						
						if att:
							for wh in att:
								if wh.employee == i.name:
									if wh.status == "Present":
										atd = "P"
										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break
											whs = diff
										elif not wh.shift:
											print("elif cond")
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["<=",dt],"end_date":[">=",dt]},["shift_type"])
											if sa:
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break
												whs = diff
											elif not sa:
												print("else block")
												sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																employee = "{0}" and
																start_date <= "{1}" and
																end_date is NULL and
																status = "Active" and 
																docstatus = 1 """.format(i.name,dt),as_dict=1)
												if sa:
													print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													diff = shift.actual_working_hours_without_break
													whs = diff
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														shift = frappe.get_doc("Shift Type",d_shift)
														diff= shift.actual_working_hours_without_break
														whs = diff
													else:
														print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														whs = dshift.standard_working_hours


											
											
									elif wh.status == "Absent":
										atd =  "H"
										# atd_c = Fore.RED + atd
										whs = 0.0	
									elif wh.status == "On Leave":
										atd = "L"
										whs = 0.0
									elif wh.status == "Half Day":
										atd = "HD"
										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break
											whs = float(diff/2)
										
										elif not wh.shift:
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["<=",dt],"end_date":[">=",dt],"docstatus":1},["shift_type"])
											if sa:
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break
												whs = float(diff/2)
											elif not sa:
												print("else block")
												sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																employee = "{0}" and
																start_date <= "{1}" and
																end_date is NULL and
																status = "Active" and 
																docstatus = 1 """.format(i.name,dt),as_dict=1)
												if sa:
													print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													diff = shift.actual_working_hours_without_break
													whs = float(diff/2)
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														print("last_if_block_in_elif cond")
														shift = frappe.get_doc("Shift Type",d_shift)
														diff= shift.actual_working_hours_without_break
														whs = float(diff/2)
													else:
														print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														whs = float(dshift.standard_working_hours/2)
										


									elif wh.status == "Work From Home":
										atd = "WFH"
										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break
											whs = diff
										elif not wh.shift:
											print("elif cond")
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["<=",dt],"end_date":[">=",dt],"docstatus":1},["shift_type"])
											print("sa***************",sa)
											if sa:
												print("sa******************",sa)
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break
												whs = diff
											elif not sa:
												print("else block")
												sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																employee = "{0}" and
																start_date <= "{1}" and
																end_date is NULL and
																status = "Active" and 
																docstatus = 1 """.format(i.name,dt),as_dict=1)
												if sa:
													print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													diff = shift.actual_working_hours_without_break
													whs = diff
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														print("last_if_block_in_elif cond in wfh condiiton")
														shift = frappe.get_doc("Shift Type",d_shift)
														diff= shift.actual_working_hours_without_break
														whs = diff
													else:
														print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														whs = dshift.standard_working_hours
										

									
									whc = dt+ "_" + "wh"
									atdn = dt+ "_"+ "att"

									dynamic.update({
										whc:whs,
										atdn:atd
									})
									
						
						else:
							sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["<=",dt],"end_date":[">=",dt]},["shift_type"])
							if sa:
								shift = frappe.get_doc("Shift Type",sa)
								diff = shift.actual_working_hours_without_break
								whs = diff
							elif not sa:
								print("else block")
								sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
													employee = "{0}" and
													start_date <= "{1}" and
													end_date is NULL and
													status = "Active" and 
													docstatus = 1 """.format(i.name,dt),as_dict=1)
								if sa:
									print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
									shift = frappe.get_doc("Shift Type",sa[0].shift_type)
									diff = shift.actual_working_hours_without_break
									whs = diff
								else:
									d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
									if d_shift:
										shift = frappe.get_doc("Shift Type",d_shift)
										diff= shift.actual_working_hours_without_break
										whs = diff
									else:
										print("last_else_block_in_elif cond")
										dshift = frappe.get_doc("HR Settings")
										whs = dshift.standard_working_hours

							
							whc = dt+ "_"+ "wh"
							atdn = dt +"_"+ "att"
							atd = "UA"

							
							dynamic.update({
										whc:whs,
										atdn:atd

									})

						alloc = frappe.db.get_all("Resource Allocation",alloc_filters,['sum(allocation) as allocation','primary_consultance','rup'])
						if alloc:
							for j in  alloc:
								if j.primary_consultance == i.name:
									allocation = dt+ "_" + "alloc"
									alc = j.allocation
									rup = dt + "_" + "rup"
									p = j.rup

									dynamic.update({
										allocation:alc,
										rup:p
									})

						act=frappe.db.sql(""" select sum(ti.hours) as hours , t.employee as emp from `tabTimesheet` t 
													join `tabTimesheet Detail` ti
												on ti.parent=t.name where date(from_time)="{0}"and t.employee="{1}"  and t.docstatus = 1 """.format(dt,i.name),as_dict = 1)
						if act:

							for k in act:
								if k.emp == i.name:
									actual = dt +"_" + 'aw'
									aw = k.hours 

									dynamic.update({
										actual:aw 
									})

						billable=frappe.db.sql(""" select sum(ti.billing_hours) as hours , t.employee as emp from `tabTimesheet` t 
													join `tabTimesheet Detail` ti
												on ti.parent=t.name where date(from_time)="{0}"and t.employee="{1}"  and t.docstatus = 1""".format(dt,i.name),as_dict = 1)
						if billable:
							# print(act)
							for k in billable:
								if k.emp == i.name:
									billh = dt+ "_" + 'bw'
									bw = k.hours
									

									dynamic.update({
										billh:bw 
									})


				eps.append(dynamic)	
			if filters.get("periodicity") == "Weekly":
				# holiday()
				week_date_ranges = []
				current_date = datetime.datetime.strptime(filters.get("from_date"), "%Y-%m-%d")

				while current_date <= datetime.datetime.strptime(filters.get("to_date"), "%Y-%m-%d"):
					# print("current_date", current_date)
					to_date = current_date + datetime.timedelta(days=6)
					week_date_ranges.append({
						"from_date": current_date.strftime("%Y-%m-%d"),
						"to_date": to_date.strftime("%Y-%m-%d")
					})
					current_date += datetime.timedelta(weeks=1)

				for dt in week_date_ranges:
					whs=0
					p=0
					alc=0
					# from datetime import date, timedelta
					d1 = getdate(dt.get("from_date"))
					d2 = getdate(dt.get("to_date"))
					d = d2-d1
					stu=[]
					for kl in range(d.days + 1):
						day = d1 + timedelta(days=kl)
						if getdate(day)<=getdate(filters.get("to_date")) and getdate(day)>=getdate(filters.get("from_date")):
							if getdate(day) not in holiday:
								att_filters = {'employee':i.name,'attendance_date':day,'docstatus':1}							
								att = frappe.db.get_all("Attendance",att_filters,["employee","status","shift","attendance_date"])
								
								if att:
									for wh in att:
										if wh.employee == i.name:
											if wh.status == "Present":
												atd = "P"

												if wh.shift :
													shift = frappe.get_doc("Shift Type",wh.shift)
													diff= shift.actual_working_hours_without_break
													whs += diff
												elif not wh.shift:
													print("elif cond")
													sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]]},["shift_type"])
													if sa:
														
														shift = frappe.get_doc("Shift Type",sa)
														diff = shift.actual_working_hours_without_break
														whs += diff
													elif not sa:
														print("else block")
														query = """
															SELECT shift_type
															FROM `tabShift Assignment`
															WHERE employee = %s
																AND start_date >= %s
																AND (end_date IS NULL OR end_date >= %s)
																AND status = 'Active'
																AND docstatus = 1
														"""
														
														assignments = frappe.db.sql(query, (i.name, filters.get("from_date"), filters.get("to_date")), as_dict=True)

														if sa:
															print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
															shift = frappe.get_doc("Shift Type",sa[0].shift_type)
															diff = shift.actual_working_hours_without_break
															whs += diff
														else:
															d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
															if d_shift:
																shift = frappe.get_doc("Shift Type",d_shift)
																diff= shift.actual_working_hours_without_break
																whs += diff
															else:
																print("last_else_block_in_elif cond")
																dshift = frappe.get_doc("HR Settings")
																whs += dshift.standard_working_hours


													
													
											elif wh.status == "Absent":
												atd =  "H"
												whs += 0.0	
											elif wh.status == "On Leave":
												atd = "L"
												whs += 0.0
											elif wh.status == "Half Day":
												atd = "HD"
												if wh.shift :
													shift = frappe.get_doc("Shift Type",wh.shift)
													diff= shift.actual_working_hours_without_break
													whst = float(diff/2)
													whs +=shift.actual_working_hours_without_break-whst
												
												elif not wh.shift:
													print("elif cond")
													sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]],"docstatus":1},["shift_type"])
													if sa:
														shift = frappe.get_doc("Shift Type",sa)
														diff = shift.actual_working_hours_without_break
														whst = float(diff/2)
														whs+=shift.actual_working_hours_without_break-whst
													elif not sa:
														print("else block")
														sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																		employee = "{0}" and
																		start_date between "{1}" and "{2}" and
																		end_date is NULL and
																		status = "Active" and 
																		docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
														if sa:
															print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
															shift = frappe.get_doc("Shift Type",sa[0].shift_type)
															diff = shift.actual_working_hours_without_break
															whst = float(diff/2)
															whs+=shift.actual_working_hours_without_break-whst
														else:
															d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
															if d_shift:
																print("last_if_block_in_elif cond")
																shift = frappe.get_doc("Shift Type",d_shift)
																diff= shift.actual_working_hours_without_break
																whst = float(diff/2)
																whs+=shift.actual_working_hours_without_break-whst
															else:
																print("last_else_block_in_elif cond")
																dshift = frappe.get_doc("HR Settings")
																whst = float(dshift.standard_working_hours/2)
																whs+=shift.actual_working_hours_without_break-whst
												


											elif wh.status == "Work From Home":
												atd = "WFH"
												if wh.shift :
													shift = frappe.get_doc("Shift Type",wh.shift)
													diff= shift.actual_working_hours_without_break
													whs += diff
												elif not wh.shift:
													print("elif cond")
													sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]],"docstatus":1},["shift_type"])
													if sa:
														shift = frappe.get_doc("Shift Type",sa)
														diff = shift.actual_working_hours_without_break
														whs += diff
													elif not sa:
														print("else block")
														sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																		employee = "{0}" and
																		start_date between "{1}" and "{2}"and
																		end_date is NULL and
																		status = "Active" and 
																		docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
														if sa:
															shift = frappe.get_doc("Shift Type",sa[0].shift_type)
															diff = shift.actual_working_hours_without_break
															whs += diff
														else:
															d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
															if d_shift:
																print("last_if_block_in_elif cond in wfh condiiton")
																shift = frappe.get_doc("Shift Type",d_shift)
																print("shift type if wala",shift)
																diff= shift.actual_working_hours_without_break
																whs += diff
															else:
																print("last_else_block_in_elif cond")
																dshift = frappe.get_doc("HR Settings")
																print("shift type if wala",dshift)
																whs += dshift.standard_working_hours
												

											
											
								else:
									sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]]},["shift_type"])
								
									if sa:
										shift = frappe.get_doc("Shift Type",sa)
										diff = shift.actual_working_hours_without_break
										whs += diff
									elif not sa:
										sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
															employee = "{0}" and
															start_date between "{1}" and "{2}" and
															end_date is NULL and
															status = "Active" and 
															docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
										if sa:
											shift = frappe.get_doc("Shift Type",sa[0].shift_type)
											diff = shift.actual_working_hours_without_break
											whs += diff
										else:
											d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
											if d_shift:
												shift = frappe.get_doc("Shift Type",d_shift)
												diff= shift.actual_working_hours_without_break
												whs += diff
											else:
												dshift = frappe.get_doc("HR Settings")
												whs += dshift.standard_working_hours

								atd = "UA"
								alloc_filters = {'date':getdate(day),'primary_consultance':i.name}
								alloc = frappe.db.get_all("Resource Allocation",alloc_filters,['sum(allocation) as allocation','primary_consultance','rup'])
								if alloc:
									for j in  alloc:
										if j.primary_consultance == i.name:
											alc += j.allocation
											p += j.rup

										
					whc = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+ "_"+ "wh"
					atdn = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_"+ "att"
					rup = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + "rup"
					allocation = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + "alloc"


					dynamic.update({
								whc:whs,
								atdn:atd,
								allocation:alc,
								rup: p
							})

					

					act=frappe.db.sql(""" select sum(ti.hours) as hours , t.employee as emp from `tabTimesheet` t 
												join `tabTimesheet Detail` ti
											on ti.parent=t.name where date(from_time)>="{0}"  and date(to_time)<="{1}" and t.employee="{2}"  and t.docstatus = 1 """.format(dt.get("from_date"),dt.get("to_date"),i.name),as_dict = 1)
					if act:
						for k in act:
							if k.emp == i.name:
								actual = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + 'aw'
								aw = k.hours 

								dynamic.update({
									actual:aw 
								})

					billable=frappe.db.sql(""" select sum(ti.billing_hours) as hours , t.employee as emp from `tabTimesheet` t 
												join `tabTimesheet Detail` ti
											on ti.parent=t.name where date(from_time)>="{0}"  and date(to_time)<="{1}" and t.employee="{2}"  and t.docstatus = 1 """.format(dt.get("from_date"),dt.get("to_date"),i.name),as_dict = 1)
					if billable:
						for k in billable:
							if k.emp == i.name:
								billh = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" +'bw'
								bw = k.hours
								

								dynamic.update({
									billh:bw 
								})

				eps.append(dynamic)

			if filters.get("periodicity") == "Monthly":
				month_date_ranges = []
				start_date_str = filters.get("from_date")
				end_date_str = filters.get("to_date")

				start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
				end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

				# Create a while loop to iterate through the months
				current_date = start_date
				while current_date <= end_date:
					month_start = current_date.replace(day=1)
					if current_date.month == 12:
						next_month = current_date.replace(year=current_date.year + 1, month=1)
					else:
						next_month = current_date.replace(month=current_date.month + 1)
					month_end = (next_month - timedelta(days=1))
					
					month_date_ranges.append({
						"from_date": month_start.strftime("%Y-%m-%d"),
						"to_date": month_end.strftime("%Y-%m-%d")
					})
					
					current_date = next_month

				for dt in month_date_ranges:
					whs=0
					p=0
					alc=0
					# from datetime import date, timedelta
					d1 = getdate(dt.get("from_date"))
					d2 = getdate(dt.get("to_date"))
					d = d2-d1
					for kl in range(d.days + 1):
						day = d1 + timedelta(days=kl)
						
						att_filters = {'employee':i.name,'attendance_date':getdate(day),'docstatus':1}
						att = frappe.db.get_all("Attendance",att_filters,["employee","status","shift","attendance_date"])
						if getdate(day) not in holiday:
							print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&",att)
							if att:
								for wh in att:
									if wh.status == "Present":
										atd = "P"
										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break
											whs += diff
										elif not wh.shift:
											print("elif cond")
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]]},["shift_type"])
											if sa:
												
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break*1
												whs += diff
											elif not sa:
												print("else block")
												query = """
													SELECT shift_type
													FROM `tabShift Assignment`
													WHERE employee = %s
														AND start_date >= %s
														AND (end_date IS NULL OR end_date >= %s)
														AND status = 'Active'
														AND docstatus = 1
												"""
												
												assignments = frappe.db.sql(query, (i.name, filters.get("from_date"), filters.get("to_date")), as_dict=True)

												if sa:
													print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													diff = shift.actual_working_hours_without_break
													whs += diff
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														shift = frappe.get_doc("Shift Type",d_shift)
														diff= shift.actual_working_hours_without_break
														whs += diff
													else:
														print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														whs += dshift.standard_working_hours


											
											
									elif wh.status == "Absent":
										atd =  "H"
										whs += 0.0	
									elif wh.status == "On Leave":
										atd = "L"
										whs += 0.0
									elif wh.status == "Half Day":
										atd = "HD"
										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break
											whst = float(diff/2)
											whs +=shift.actual_working_hours_without_break-whst
										
										elif not wh.shift:
											print("elif cond")
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]],"docstatus":1},["shift_type"])
											if sa:
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break
												whst = float(diff/2)
												whs +=shift.actual_working_hours_without_break-whst
											elif not sa:
												print("else block")
												sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																employee = "{0}" and
																start_date between "{1}" and "{2}" and
																end_date is NULL and
																status = "Active" and 
																docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
												if sa:
													print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													diff = shift.actual_working_hours_without_break
													whst = float(diff/2)
													whs +=shift.actual_working_hours_without_break-whst
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														print("last_if_block_in_elif cond")
														shift = frappe.get_doc("Shift Type",d_shift)
														diff= shift.actual_working_hours_without_break
														whst = float(diff/2)
														whs +=shift.actual_working_hours_without_break-whst
													else:
														print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														whst = float(dshift.standard_working_hours/2)
														whs +=shift.actual_working_hours_without_break-whst
										


									elif wh.status == "Work From Home":
										atd = "WFH"
										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break
											whs += diff
										elif not wh.shift:
											print("elif cond")
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]],"docstatus":1},["shift_type"])
											if sa:
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break
												whs += diff
											elif not sa:
												print("else block")
												sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																employee = "{0}" and
																start_date between "{1}" and "{2}"and
																end_date is NULL and
																status = "Active" and 
																docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
												if sa:
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													diff = shift.actual_working_hours_without_break
													whs += diff
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														print("last_if_block_in_elif cond in wfh condiiton")
														shift = frappe.get_doc("Shift Type",d_shift)
														print("shift type if wala",shift)
														diff= shift.actual_working_hours_without_break
														whs += diff
													else:
														print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														print("shift type if wala",dshift)
														whs += dshift.standard_working_hours
							else:
								sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]]},["shift_type"])
								if sa:
									shift = frappe.get_doc("Shift Type",sa)
									diff = shift.actual_working_hours_without_break
									whs += diff
								elif not sa:
									sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
														employee = "{0}" and
														start_date between "{1}" and "{2}" and
														end_date is NULL and
														status = "Active" and 
														docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
									if sa:
										shift = frappe.get_doc("Shift Type",sa[0].shift_type)
										diff = shift.actual_working_hours_without_break
										whs += diff
									else:
										d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
										if d_shift:
											shift = frappe.get_doc("Shift Type",d_shift)
											diff= shift.actual_working_hours_without_break
											whs += diff
										else:
											dshift = frappe.get_doc("HR Settings")
											whs += dshift.standard_working_hours
							print(whs)
							atd = "UA"
							alloc_filters = {'date':day,'primary_consultance':i.name}
							alloc = frappe.db.get_all("Resource Allocation",alloc_filters,['sum(allocation) as allocation','primary_consultance','rup'])
							if alloc:
								for j in  alloc:
									if j.primary_consultance == i.name:
										alc +=j.allocation
										p += j.rup

					allocation = str(dt.get("from_date")) + "-" + str(dt.get("to_date")) + "_alloc"
					rup = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + 'rup'
					whc = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+ "_wh"
					atdn = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_att"
					
					dynamic.update({
								whc:whs,
								atdn:atd,
								allocation:alc,
								rup: p
							})

					act=frappe.db.sql(""" select sum(ti.hours) as hours , t.employee as emp from `tabTimesheet` t 
												join `tabTimesheet Detail` ti
											on ti.parent=t.name where date(from_time)>="{0}"  and date(to_time)<="{1}" and t.employee="{2}"  and t.docstatus = 1 """.format(dt.get("from_date"),dt.get("to_date"),i.name),as_dict = 1)
					if act:
						
						for k in act:
							if k.emp == i.name:
								actual = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + 'aw'
								aw = k.hours 
								# print("$$$$$$$$$$$$$$$$$$$$$$$$$",actual,aw)
								dynamic.update({
									actual:aw 
								})

					billable=frappe.db.sql(""" select sum(ti.billing_hours) as hours , t.employee as emp from `tabTimesheet` t 
												join `tabTimesheet Detail` ti
											on ti.parent=t.name where date(from_time)>="{0}"  and date(to_time)<="{1}" and t.employee="{2}"  and t.docstatus = 1 """.format(dt.get("from_date"),dt.get("to_date"),i.name),as_dict = 1)
					if billable:
						for k in billable:
							if k.emp == i.name:
								billh = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+ "_" + 'bw'
								bw = k.hours
								dynamic.update({
									billh:bw 
								})


				eps.append(dynamic)
			
			if filters.get("periodicity") == "Fortnightly":
				month_date_ranges = []
				interval = timedelta(days=14)

				# Initialize a list to store the date ranges
				start_date=getdate(filters.get("from_date"))
				end_date=getdate(filters.get("to_date"))
				# Start from the first date and keep adding the interval until you reach the end date
				while start_date <= end_date:
					# Calculate the end date for the current range
					end_of_fortnight = start_date + interval - timedelta(days=1)
					
					# Ensure the end date does not exceed the end_date
					if end_of_fortnight > end_date:
						end_of_fortnight = end_date
					
					# Add the current date range to the list
					month_date_ranges.append({
						"from_date": start_date.strftime("%Y-%m-%d"),
						"to_date": end_of_fortnight.strftime("%Y-%m-%d")
					})
					
					# Move to the next fortnight
					start_date = end_of_fortnight + timedelta(days=1)
					print("$$$$$$$$$$$$$$$$$$$$$$$$$$$",month_date_ranges)

				for dt in month_date_ranges:
					whs=0
					p=0
					alc=0
					# from datetime import date, timedelta
					d1 = getdate(dt.get("from_date"))
					d2 = getdate(dt.get("to_date"))
					d = d2-d1
					stu=[]
					for kl in range(d.days + 1):
						day = d1 + timedelta(days=kl)
						if getdate(day)<=getdate(filters.get("to_date")) and getdate(day)>=getdate(filters.get("from_date")):
							if getdate(day) not in holiday:
								att_filters = {'employee':i.name,'attendance_date':day,'docstatus':1}							
								att = frappe.db.get_all("Attendance",att_filters,["employee","status","shift","attendance_date"])
								
								if att:
									for wh in att:
										if wh.employee == i.name:
											if wh.status == "Present":
												atd = "P"

												if wh.shift :
													shift = frappe.get_doc("Shift Type",wh.shift)
													diff= shift.actual_working_hours_without_break
													whs += diff
												elif not wh.shift:
													print("elif cond")
													sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]]},["shift_type"])
													if sa:
														
														shift = frappe.get_doc("Shift Type",sa)
														diff = shift.actual_working_hours_without_break
														whs += diff
													elif not sa:
														print("else block")
														query = """
															SELECT shift_type
															FROM `tabShift Assignment`
															WHERE employee = %s
																AND start_date >= %s
																AND (end_date IS NULL OR end_date >= %s)
																AND status = 'Active'
																AND docstatus = 1
														"""
														
														assignments = frappe.db.sql(query, (i.name, filters.get("from_date"), filters.get("to_date")), as_dict=True)

														if sa:
															print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
															shift = frappe.get_doc("Shift Type",sa[0].shift_type)
															diff = shift.actual_working_hours_without_break
															whs += diff
														else:
															d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
															if d_shift:
																shift = frappe.get_doc("Shift Type",d_shift)
																diff= shift.actual_working_hours_without_break
																whs += diff
															else:
																print("last_else_block_in_elif cond")
																dshift = frappe.get_doc("HR Settings")
																whs += dshift.standard_working_hours


													
													
											elif wh.status == "Absent":
												atd =  "H"
												whs += 0.0	
											elif wh.status == "On Leave":
												atd = "L"
												whs += 0.0
											elif wh.status == "Half Day":
												atd = "HD"
												if wh.shift :
													shift = frappe.get_doc("Shift Type",wh.shift)
													diff= shift.actual_working_hours_without_break
													whst = float(diff/2)
													whs +=shift.actual_working_hours_without_break-whst
												
												elif not wh.shift:
													print("elif cond")
													sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]],"docstatus":1},["shift_type"])
													if sa:
														shift = frappe.get_doc("Shift Type",sa)
														diff = shift.actual_working_hours_without_break
														whst = float(diff/2)
														whs+=shift.actual_working_hours_without_break-whst
													elif not sa:
														print("else block")
														sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																		employee = "{0}" and
																		start_date between "{1}" and "{2}" and
																		end_date is NULL and
																		status = "Active" and 
																		docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
														if sa:
															print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
															shift = frappe.get_doc("Shift Type",sa[0].shift_type)
															diff = shift.actual_working_hours_without_break
															whst = float(diff/2)
															whs+=shift.actual_working_hours_without_break-whst
														else:
															d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
															if d_shift:
																print("last_if_block_in_elif cond")
																shift = frappe.get_doc("Shift Type",d_shift)
																diff= shift.actual_working_hours_without_break
																whst = float(diff/2)
																whs+=shift.actual_working_hours_without_break-whst
															else:
																print("last_else_block_in_elif cond")
																dshift = frappe.get_doc("HR Settings")
																whst = float(dshift.standard_working_hours/2)
																whs+=shift.actual_working_hours_without_break-whst
												


											elif wh.status == "Work From Home":
												atd = "WFH"
												if wh.shift :
													shift = frappe.get_doc("Shift Type",wh.shift)
													diff= shift.actual_working_hours_without_break
													whs += diff
												elif not wh.shift:
													print("elif cond")
													sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]],"docstatus":1},["shift_type"])
													if sa:
														shift = frappe.get_doc("Shift Type",sa)
														diff = shift.actual_working_hours_without_break
														whs += diff
													elif not sa:
														print("else block")
														sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																		employee = "{0}" and
																		start_date between "{1}" and "{2}"and
																		end_date is NULL and
																		status = "Active" and 
																		docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
														if sa:
															shift = frappe.get_doc("Shift Type",sa[0].shift_type)
															diff = shift.actual_working_hours_without_break
															whs += diff
														else:
															d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
															if d_shift:
																print("last_if_block_in_elif cond in wfh condiiton")
																shift = frappe.get_doc("Shift Type",d_shift)
																print("shift type if wala",shift)
																diff= shift.actual_working_hours_without_break
																whs += diff
															else:
																print("last_else_block_in_elif cond")
																dshift = frappe.get_doc("HR Settings")
																print("shift type if wala",dshift)
																whs += dshift.standard_working_hours
												

											
											
								else:
									sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]]},["shift_type"])
								
									if sa:
										shift = frappe.get_doc("Shift Type",sa)
										diff = shift.actual_working_hours_without_break
										whs += diff
									elif not sa:
										sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
															employee = "{0}" and
															start_date between "{1}" and "{2}" and
															end_date is NULL and
															status = "Active" and 
															docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
										if sa:
											shift = frappe.get_doc("Shift Type",sa[0].shift_type)
											diff = shift.actual_working_hours_without_break
											whs += diff
										else:
											d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
											if d_shift:
												shift = frappe.get_doc("Shift Type",d_shift)
												diff= shift.actual_working_hours_without_break
												whs += diff
											else:
												dshift = frappe.get_doc("HR Settings")
												whs += dshift.standard_working_hours

								atd = "UA"
								alloc_filters = {'date':getdate(day),'primary_consultance':i.name}
								alloc = frappe.db.get_all("Resource Allocation",alloc_filters,['sum(allocation) as allocation','primary_consultance','rup'])
								if alloc:
									for j in  alloc:
										if j.primary_consultance == i.name:
											alc += j.allocation
											p += j.rup

										
					whc = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+ "_"+ "wh"
					atdn = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_"+ "att"
					rup = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + "rup"
					allocation = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + "alloc"


					dynamic.update({
								whc:whs,
								atdn:atd,
								allocation:alc,
								rup: p
							})

					

					act=frappe.db.sql(""" select sum(ti.hours) as hours , t.employee as emp from `tabTimesheet` t 
												join `tabTimesheet Detail` ti
											on ti.parent=t.name where date(from_time)>="{0}"  and date(to_time)<="{1}" and t.employee="{2}"  and t.docstatus = 1 """.format(dt.get("from_date"),dt.get("to_date"),i.name),as_dict = 1)
					if act:
						for k in act:
							if k.emp == i.name:
								actual = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + 'aw'
								aw = k.hours 

								dynamic.update({
									actual:aw 
								})

					billable=frappe.db.sql(""" select sum(ti.billing_hours) as hours , t.employee as emp from `tabTimesheet` t 
												join `tabTimesheet Detail` ti
											on ti.parent=t.name where date(from_time)>="{0}"  and date(to_time)<="{1}" and t.employee="{2}"  and t.docstatus = 1 """.format(dt.get("from_date"),dt.get("to_date"),i.name),as_dict = 1)
					if billable:
						for k in billable:
							if k.emp == i.name:
								billh = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" +'bw'
								bw = k.hours
								

								dynamic.update({
									billh:bw 
								})

				eps.append(dynamic)
			

			if filters.get("periodicity") == "Yearly":
				print("==================jkdjfkdjfkdflksjfsjfd")
				year_date_ranges = []
				from_date= getdate(filters.get("from_date"))
				to_date= getdate(filters.get("to_date"))

				# from_date = datetime.datetime.strptime(from_date_str, "%d-%m-%Y")
				# to_date = datetime.datetime.strptime(to_date_str, "%d-%m-%Y")


				while from_date.year <= to_date.year:
					start_date = from_date.replace(month=1, day=1)
					end_date = from_date.replace(month=12, day=31)
					
					if from_date.year == to_date.year:
						end_date = to_date
					
					year_date_ranges.append({"from_date": start_date.strftime("%d-%m-%Y"), "to_date": end_date.strftime("%d-%m-%Y")})
					
					from_date = from_date.replace(year=from_date.year + 1)


				columns = []

				for dt in year_date_ranges:

									
						att_filters = {'employee':i.name,'attendance_date':["between",[dt.get("from_date"),dt.get("to_date")]],'docstatus':1}
						alloc_filters = {'date':["between",[dt.get("from_date"),dt.get("to_date")]],'primary_consultance':i.name}
						
						att = frappe.db.get_all("Attendance",att_filters,["employee","status","shift"])
						
						if att:
							for wh in att:
								if wh.employee == i.name:
									if wh.status == "Present":
										atd = "P"

										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break * (365-len(holiday))
											whs = diff
										elif not wh.shift:
											print("elif cond")
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]]},["shift_type"])
											# print("sa***************",sa)
											if sa:
												# print("sa******************",sa)
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break * (365-len(holiday))
												whs = diff
											elif not sa:
												print("else block")
												query = """
													SELECT shift_type
													FROM `tabShift Assignment`
													WHERE employee = %s
														AND start_date >= %s
														AND (start_date IS NULL OR end_date >= %s)
														AND status = 'Active'
														AND docstatus = 1
												"""
												
												assignments = frappe.db.sql(query, (i.name, filters.get("from_date"), filters.get("to_date")), as_dict=True)

												if sa:
													print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													print("======jjjjj",shift)
													diff = shift.actual_working_hours_without_break * (365-len(holiday))
													whs = diff
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														shift = frappe.get_doc("Shift Type",d_shift)
														print("else walapppp=",shift)
														diff= shift.actual_working_hours_without_break * (365-len(holiday))
														whs = diff
													else:
														# print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														print("======iiiiiielsesewes",dshift)
														whs = dshift.standard_working_hours


											
											
									elif wh.status == "Absent":
										atd =  "H"
										# atd_c = Fore.RED + atd
										whs = 0.0	
									elif wh.status == "On Leave":
										atd = "L"
										whs = 0.0
									elif wh.status == "Half Day":
										atd = "HD"
										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break
											whs = float(diff/2)
										
										elif not wh.shift:
											print("elif cond")
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]],"docstatus":1},["shift_type"])
											# print("sa***************",sa)
											if sa:
												# print("sa******************",sa)
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break * (365-len(holiday))
												whs = float(diff/2)
											elif not sa:
												print("else block")
												sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																employee = "{0}" and
																start_date between "{1}" and "{2}" and
																end_date is NULL and
																status = "Active" and 
																docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
												if sa:
													print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													diff = shift.actual_working_hours_without_break * (365-len(holiday))
													whs = float(diff/2)
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														print("last_if_block_in_elif cond")
														shift = frappe.get_doc("Shift Type",d_shift)
														diff= shift.actual_working_hours_without_break * (365-len(holiday))
														whs = float(diff/2)
													else:
														print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														whs = float(dshift.standard_working_hours/2)
										


									elif wh.status == "Work From Home":
										atd = "WFH"
										if wh.shift :
											shift = frappe.get_doc("Shift Type",wh.shift)
											diff= shift.actual_working_hours_without_break * (365-len(holiday))
											whs = diff
										elif not wh.shift:
											print("elif cond")
											sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]],"docstatus":1},["shift_type"])
											# print("sa***************",sa)
											if sa:
												# print("sa******************",sa)
												shift = frappe.get_doc("Shift Type",sa)
												diff = shift.actual_working_hours_without_break * (365-len(holiday))
												whs = diff
											elif not sa:
												print("else block")
												sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
																employee = "{0}" and
																start_date between "{1}" and "{2}"and
																end_date is NULL and
																status = "Active" and 
																docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
												if sa:
													print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
													shift = frappe.get_doc("Shift Type",sa[0].shift_type)
													diff = shift.actual_working_hours_without_break * (365-len(holiday))
													whs = diff
												else:
													d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
													if d_shift:
														print("last_if_block_in_elif cond in wfh condiiton")
														shift = frappe.get_doc("Shift Type",d_shift)
														diff= shift.actual_working_hours_without_break * (365-len(holiday))
														whs = diff
													else:
														print("last_else_block_in_elif cond")
														dshift = frappe.get_doc("HR Settings")
														whs = dshift.standard_working_hours
										

									
									whc = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+ "_" + "wh"
									atdn = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+ "_"+ "att"

									dynamic.update({
										whc:whs,
										atdn:atd
									})
						
						else:
							sa = frappe.db.get_value("Shift Assignment",{"employee":i.name,"status":"Active","start_date":["between",[dt.get("from_date"),dt.get("to_date")]],"end_date":["between",[dt.get("from_date"),dt.get("to_date")]]},["shift_type"])
							if sa:
								shift = frappe.get_doc("Shift Type",sa)
								diff = shift.actual_working_hours_without_break * (365-len(holiday))
								whs = diff
							elif not sa:
								print("else block")
								sa = frappe.db.sql("""select shift_type from `tabShift Assignment` where 
													employee = "{0}" and
													start_date between "{1}" and "{2}" and
													end_date is NULL and
													status = "Active" and 
													docstatus = 1 """.format(i.name,dt.get("from_date"),dt.get("to_date")),as_dict=1)
								if sa:
									print("first_if_block_in_elif cond in Shift Assignment",sa,type(sa))
									shift = frappe.get_doc("Shift Type",sa[0].shift_type)
									diff = shift.actual_working_hours_without_break * (365-len(holiday))
									whs = diff
								else:
									d_shift = frappe.db.get_value("Employee",{'name':i.name},["default_shift"])
									if d_shift:
										shift = frappe.get_doc("Shift Type",d_shift)
										diff= shift.actual_working_hours_without_break * (365-len(holiday))
										whs = diff
									else:
										print("last_else_block_in_elif cond")
										dshift = frappe.get_doc("HR Settings")
										whs = dshift.standard_working_hours

							
							whc = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+ "_"+ "wh"
							atdn = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_"+ "att"
							atd = "UA"

							
							dynamic.update({
										whc:whs,
										atdn:atd

									})





						alloc = frappe.db.get_all("Resource Allocation",alloc_filters,['sum(allocation) as allocation','primary_consultance','rup'])
						if alloc:
							for j in  alloc:
								if j.primary_consultance == i.name:
									allocation = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + "alloc"
									alc = j.allocation
									rup = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + "rup"
									p = j.rup

									dynamic.update({
										allocation:alc,
										rup:p
									})

						act=frappe.db.sql(""" select sum(ti.hours) as hours , t.employee as emp from `tabTimesheet` t 
													join `tabTimesheet Detail` ti
												on ti.parent=t.name where date(from_time)>="{0}"  and date(to_time)<="{1}" and t.employee="{2}"  and t.docstatus = 1 """.format(getdate(dt.get("from_date")),getdate(dt.get("to_date")),i.name),as_dict = 1)
						
						print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",dt.get("from_date"),dt.get("to_date"),i.name)
						if act:
							for k in act:
								if k.emp == i.name:
									actual = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+"_" + 'aw'
									aw = k.hours 

									dynamic.update({
										actual:aw 
									})

						billable=frappe.db.sql(""" select sum(ti.billing_hours) as hours , t.employee as emp from `tabTimesheet` t 
													join `tabTimesheet Detail` ti
												on ti.parent=t.name where date(from_time)>="{0}"  and date(to_time)<="{1}" and t.employee="{2}"  and t.docstatus = 1 """.format(getdate(dt.get("from_date")),getdate(dt.get("to_date")),i.name),as_dict = 1)
						if billable:
							for k in billable:
								if k.emp == i.name:
									billh = str(dt.get("from_date"))+"-"+str(dt.get("to_date"))+ "_" + 'bw'
									bw = k.hours
									

									dynamic.update({
										billh:bw 
									})



					

				eps.append(dynamic)
		
								
		return eps
	
def get_chart_data(data,filters,periodicity):
	print("data",data)
	sep = "_"
	
	d_list = []
	b_list = []
	all_dts = []
	billable = ""
	actual = ""
	allocation = ""
	wh = ""
	if filters.get("from_date") and filters.get("to_date"):
		sd = filters.get('from_date')
		ed=filters.get('to_date')
		d_list.append(sd)
		d_list.append(ed)

		
		dtst = [d.date() for d in pd.to_datetime(d_list)]
		stdt=dtst[0]
		edt=dtst[1]
		date_d = (edt - stdt).days + 1
		for i in range(date_d):
			all_dts.append(add_to_date(stdt,days=i,as_string = True))

	
	

	value3 = []
	value4 = []
	value = []
	value2 = []
	labels = []
	if filters.get("periodicity")=="Daily":
		for q in all_dts:
			sum_alloc = 0.0
			sum_billable = 0.0
			sum_actual = 0.0
			sum_wh = 0.0
			labels.append(q)
			billable = q +"_" + "bw"
			actual = q +"_" + "aw"
			allocation = q +"_" + "alloc"
			wh = q +"_"+ "wh"

			if data:
				for i in data:
			
					sum_billable += i.get(billable) if i.get(billable) else 0

					sum_billable_f = "{:.2f}".format(sum_billable)
				
					sum_actual += i.get(actual) if i.get(actual) else 0

					sum_actual_f = "{:.2f}".format(sum_actual)
				
					sum_alloc += i.get(allocation) if i.get(allocation) else 0

					sum_alloc_f = "{:.2f}".format(sum_alloc)
				
					sum_wh += i.get(wh) if i.get(wh) else 0

					sum_wh_f = "{:.2f}".format(sum_wh)

				value.append(sum_billable_f)
				value2.append(sum_actual_f)
				value3.append(sum_alloc_f)
				value4.append(sum_wh_f)

		datasets1 = []
		
		if value4:
			datasets1.append({'name': ('Working Hours'), 'values': value4})

		if value3:
			datasets1.append({'name': ('Allocation'), 'values': value3})
		
		if value2:
			datasets1.append({'name': ('Timesheet Hours'), 'values': value2})

		if value:
			datasets1.append({'name': ('Billable Hours'), 'values': value,'chartType':'line'})
		

		chart1 = {
			"data": {
				'labels': labels,
				'datasets': datasets1
			},
		}
		chart1["type"] = "bar"

		print("****************************",chart1)
		return chart1
	if filters.get("periodicity") == "Weekly":
		week_date_ranges = []
		current_date = datetime.datetime.strptime(filters.get("from_date"), "%Y-%m-%d")

		while current_date <= datetime.datetime.strptime(filters.get("to_date"), "%Y-%m-%d"):
			print("current_date", current_date)
			to_date = current_date + datetime.timedelta(days=6)
			week_date_ranges.append({
				"from_date": current_date.strftime("%Y-%m-%d"),
				"to_date": to_date.strftime("%Y-%m-%d")
			})
			current_date += datetime.timedelta(weeks=1) 
			
		for week in week_date_ranges:
			sum_alloc = 0.0
			sum_billable = 0.0
			sum_actual = 0.0
			sum_wh = 0.0
			labels.append(str(week.get("from_date")) + "-" + str(week.get("to_date")))
			billable = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_bw"
			actual = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_aw"
			allocation = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_alloc"
			wh = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_wh"
			
			if data:
				for i in data:

					sum_billable += i.get(billable) if i.get(billable) else 0

					sum_billable_f = "{:.2f}".format(sum_billable)
				
					sum_actual += i.get(actual) if i.get(actual) else 0

					sum_actual_f = "{:.2f}".format(sum_actual)
				
					sum_alloc += i.get(allocation) if i.get(allocation) else 0

					sum_alloc_f = "{:.2f}".format(sum_alloc)
				
					sum_wh += i.get(wh) if i.get(wh) else 0

					sum_wh_f = "{:.2f}".format(sum_wh)

				value.append(sum_billable_f)
				value2.append(sum_actual_f)
				value3.append(sum_alloc_f)
				value4.append(sum_wh_f)

		datasets1 = []
		
		if value4:
			datasets1.append({'name': ('Working Hours'), 'values': value4})

		if value3:
			datasets1.append({'name': ('Allocation'), 'values': value3})
		
		if value2:
			datasets1.append({'name': ('Timesheet Hours'), 'values': value2})

		if value:
			datasets1.append({'name': ('Billable Hours'), 'values': value,'chartType':'line'})
		

		chart1 = {
			"data": {
				'labels': labels,
				'datasets': datasets1
			},
		}
		chart1["type"] = "bar"


		return chart1

	if filters.get("periodicity")=="Monthly":
		month_date_ranges = []
		start_date_str = filters.get("from_date")
		end_date_str = filters.get("to_date")

		start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
		end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

		# Create a while loop to iterate through the months
		current_date = start_date
		while current_date <= end_date:
			month_start = current_date.replace(day=1)
			if current_date.month == 12:
				next_month = current_date.replace(year=current_date.year + 1, month=1)
			else:
				next_month = current_date.replace(month=current_date.month + 1)
			month_end = (next_month - timedelta(days=1))
			
			month_date_ranges.append({
				"from_date": month_start.strftime("%Y-%m-%d"),
				"to_date": month_end.strftime("%Y-%m-%d")
			})
			
			current_date = next_month

		print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",month_date_ranges)
		for month in month_date_ranges:
			sum_alloc = 0.0
			sum_billable = 0.0
			sum_actual = 0.0
			sum_wh = 0.0
			import calendar
			mon=getdate(month.get("from_date")).month
			year=getdate(month.get("from_date")).year
			m=calendar.month_name[mon]
			labels.append(str(m) + "-" + str(year))
			billable = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"
			actual = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_aw"
			allocation = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_alloc"
			wh = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_wh"

			if data:
				for i in data:
					
					sum_billable += i.get(billable) if i.get(billable) else 0

					sum_billable_f = "{:.2f}".format(sum_billable)
				
					sum_actual += i.get(actual) if i.get(actual) else 0

					sum_actual_f = "{:.2f}".format(sum_actual)
				
					sum_alloc += i.get(allocation) if i.get(allocation) else 0

					sum_alloc_f = "{:.2f}".format(sum_alloc)
				
					sum_wh += i.get(wh) if i.get(wh) else 0

					sum_wh_f = "{:.2f}".format(sum_wh)

				value.append(sum_billable_f)
				value2.append(sum_actual_f)
				value3.append(sum_alloc_f)
				value4.append(sum_wh_f)

		datasets1 = []
		
		if value4:
			datasets1.append({'name': ('Working Hours'), 'values': value4})

		if value3:
			datasets1.append({'name': ('Allocation'), 'values': value3})
		
		if value2:
			datasets1.append({'name': ('Timesheet Hours'), 'values': value2})

		if value:
			datasets1.append({'name': ('Billable Hours'), 'values': value,'chartType':'line'})
		

		chart1 = {
			"data": {
				'labels': labels,
				'datasets': datasets1
			},
		}
		chart1["type"] = "bar"
		print("****************************",chart1)
		return chart1
	

	if filters.get("periodicity")=="Fortnightly":
		month_date_ranges = []
		interval = timedelta(days=14)

		# Initialize a list to store the date ranges
		start_date=getdate(filters.get("from_date"))
		end_date=getdate(filters.get("to_date"))
		# Start from the first date and keep adding the interval until you reach the end date
		while start_date <= end_date:
			# Calculate the end date for the current range
			end_of_fortnight = start_date + interval - timedelta(days=1)
			
			# Ensure the end date does not exceed the end_date
			if end_of_fortnight > end_date:
				end_of_fortnight = end_date
			
			# Add the current date range to the list
			month_date_ranges.append({
				"from_date": start_date.strftime("%Y-%m-%d"),
				"to_date": end_of_fortnight.strftime("%Y-%m-%d")
			})
			
			# Move to the next fortnight
			start_date = end_of_fortnight + timedelta(days=1)

		for month in month_date_ranges:
			sum_alloc = 0.0
			sum_billable = 0.0
			sum_actual = 0.0
			sum_wh = 0.0
			labels.append(str(month.get("from_date")) + "-" + str(month.get("to_date")))
			billable = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"
			actual = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_aw"
			allocation = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_alloc"
			wh = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_wh"

			if data:
				for i in data:
					
					sum_billable += i.get(billable) if i.get(billable) else 0

					sum_billable_f = "{:.2f}".format(sum_billable)
				
					sum_actual += i.get(actual) if i.get(actual) else 0

					sum_actual_f = "{:.2f}".format(sum_actual)
				
					sum_alloc += i.get(allocation) if i.get(allocation) else 0

					sum_alloc_f = "{:.2f}".format(sum_alloc)
				
					sum_wh += i.get(wh) if i.get(wh) else 0

					sum_wh_f = "{:.2f}".format(sum_wh)

				value.append(sum_billable_f)
				value2.append(sum_actual_f)
				value3.append(sum_alloc_f)
				value4.append(sum_wh_f)

		datasets1 = []
		
		if value4:
			datasets1.append({'name': ('Working Hours'), 'values': value4})

		if value3:
			datasets1.append({'name': ('Allocation'), 'values': value3})
		
		if value2:
			datasets1.append({'name': ('Timesheet Hours'), 'values': value2})

		if value:
			datasets1.append({'name': ('Billable Hours'), 'values': value,'chartType':'line'})
		

		chart1 = {
			"data": {
				'labels': labels,
				'datasets': datasets1
			},
		}
		chart1["type"] = "bar"
		print("****************************",chart1)
		return chart1
		
	
	
	if filters.get("periodicity") == "Yearly":
		year_date_ranges = []
		from_date= getdate(filters.get("from_date"))
		to_date= getdate(filters.get("to_date"))

		# from_date = datetime.datetime.strptime(from_date_str, "%d-%m-%Y")
		# to_date = datetime.datetime.strptime(to_date_str, "%d-%m-%Y")

		# yearly_dates = []

		while from_date.year <= to_date.year:
			start_date = from_date.replace(month=1, day=1)
			end_date = from_date.replace(month=12, day=31)
			
			if from_date.year == to_date.year:
				end_date = to_date
			
			year_date_ranges.append({"from_date": start_date.strftime("%d-%m-%Y"), "to_date": end_date.strftime("%d-%m-%Y")})
			
			from_date = from_date.replace(year=from_date.year + 1)
			
		labels = []
		value = []
		value2 = []
		value3 = []
		value4 = []

		for month in year_date_ranges:
			sum_billable = 0.0
			sum_actual = 0.0
			sum_alloc = 0.0
			sum_wh = 0.0
			# labels.append(f"{year['from_date']} - {year['to_date']}") 
			
			# billable = f"{year['from_date']}-{year['to_date']}_bw"
			# actual = f"{year['from_date']}-{year['to_date']}_aw"
			# allocation = f"{year['from_date']}-{year['to_date']}_alloc"
			# wh = f"{year['from_date']}-{year['to_date']}_wh"
			labels.append(str(month.get("from_date")) + "-" + str(month.get("to_date")))
			billable = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"
			actual = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_aw"
			allocation =str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_"+ 'alloc'
			wh = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_wh"
				
			
			if data:
				for i in data:
					sum_billable += i.get(billable, 0)
					sum_actual += i.get(actual, 0)
					sum_alloc += i.get(allocation, 0)
					sum_wh += i.get(wh, 0)

			value.append("{:.2f}".format(sum_billable))
			value2.append("{:.2f}".format(sum_actual))
			value3.append("{:.2f}".format(sum_alloc))
			value4.append("{:.2f}".format(sum_wh))

		datasets1 = []

		if value4:
			datasets1.append({'name': 'Working Hours', 'values': value4})

		if value3:
			datasets1.append({'name': 'Allocation', 'values': value3})

		if value2:
			datasets1.append({'name': 'Timesheet Hours', 'values': value2})

		if value:
			datasets1.append({'name': 'Billable Hours', 'values': value, 'chartType': 'line'})

		chart1 = {
			"data": {
				'labels': labels,
				'datasets': datasets1
			},
			"type": "bar"  
		}

		print("***************===================*************", chart1)
		return chart1

			

def get_summary(filters,data):
	all_dts = []
	d_list = []

	if filters.get("from_date") and filters.get("to_date"):
		sd = filters.get('from_date')
		ed=filters.get('to_date')
		d_list.append(sd)
		d_list.append(ed)

		
		dtst = [d.date() for d in pd.to_datetime(d_list)]
		stdt=dtst[0]
		edt=dtst[1]
		date_d = (edt - stdt).days + 1
		for i in range(date_d):
			all_dts.append(add_to_date(stdt,days=i,as_string = True))

		labels = []

		sum_alloc = 0.0
		sum_billable = 0.0
		sum_actual = 0.0
		sum_wh = 0.0
		sum_rup = 0.0
		sum_avg_billable = 0.0
		sum_wh_f = 0.0
		sum_actual_f  = 0.0
		sum_alloc_f = 0.0
		sum_rup_f = 0.0
		avb = 0.0
		avw=0
		tvb = 0.0
		tva=0.0
		sum_avg_billable_f = 0.0
		sum_billable_f = 0.0
		if filters.get("periodicity")=="Daily":
			for q in all_dts:
				
				labels.append(q)
				billable = q +"_" + "bw"
				actual = q +"_" + "aw"
				allocation = q +"_" + "alloc"
				wh = q +"_"+ "wh"
				rup = q + "_" + "rup"
				avg_bill = q + "_" + "bw"

				if data:
						
						for i in data:
								
							sum_billable += i.get(billable) if i.get(billable) else 0

							sum_billable_f = "{:.2f}".format(sum_billable)
						
							sum_actual += i.get(actual) if i.get(actual) else 0

							sum_actual_f = "{:.2f}".format(sum_actual)
						
							sum_alloc += i.get(allocation) if i.get(allocation) else 0

							sum_alloc_f = "{:.2f}".format(sum_alloc)
							
							sum_wh += i.get(wh) if i.get(wh) else 0

							sum_wh_f = "{:.2f}".format(sum_wh)

							sum_rup += i.get(rup) if i.get(rup) else 0

							sum_rup_f = "{:.2f}".format(sum_rup/len(data))

							sum_avg_billable += i.get(avg_bill) if i.get(avg_bill) else 0

							sum_avg_billable_f = "{:.2f}".format((sum_avg_billable/float(sum_wh_f))*100) if float(sum_wh_f)  > 0 else 0

							avb = "{:.2f}".format((float(sum_avg_billable)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0

							tvb = "{:.2f}".format((float(sum_avg_billable)/float(sum_actual_f))*100) if float(sum_actual_f) > 0 else 0

							avw = "{:.2f}".format((float(sum_alloc_f)/float(sum_wh_f))*100) if float(sum_wh_f) > 0 else 0

							tva = "{:.2f}".format((float(sum_actual_f)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0


		
			return [
				{"label":"Total Working Hours","value":sum_wh_f,'indicator':'Red'},
				{"label":"Total Allocation","value": sum_alloc_f,'indicator':'Red'},
				{"label":"Total Timesheet Hours","value": sum_actual_f,'indicator':'Red'},
				{"label":"Total Billable Hours","value":sum_billable_f,'indicator':'Red'},
				{"label":"Allocation Vs Working %","value":avw,'indicator':'Red'},
				{"label":"Timesheet Vs Allocation %","value":tva,'indicator':'Red'},
				{"label":"Billable Vs Working %","value":sum_avg_billable_f,'indicator':'Red'},
				{"label":"Billable Vs Allocation %","value":avb,'indicator':'Red'},
				{"label":"Billable Vs Timesheet %","value":tvb,'indicator':'Red'}	
			]
		
		if filters.get("periodicity") == "Weekly":
			week_date_ranges = []
			current_date = datetime.datetime.strptime(filters.get("from_date"), "%Y-%m-%d")

			while current_date <= datetime.datetime.strptime(filters.get("to_date"), "%Y-%m-%d"):
				print("current_date", current_date)
				to_date = current_date + datetime.timedelta(days=6)
				week_date_ranges.append({
					"from_date": current_date.strftime("%Y-%m-%d"),
					"to_date": to_date.strftime("%Y-%m-%d")
				})
				current_date += datetime.timedelta(weeks=1)
			print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",week_date_ranges)
			for week in week_date_ranges:
				labels.append(str(week.get("from_date")) + "-" + str(week.get("to_date")))
				billable = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_bw"
				actual = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_aw"
				allocation =str(week.get("from_date"))+"-"+str(week.get("to_date"))+"_"+ 'alloc'
				# 2023-06-28-2023-07-04_alloc

				wh = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_wh"
				rup = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_rup"
				avg_bill = str(week.get("from_date")) + "-" + str(week.get("to_date")) + "_bw"

				if data:
					print("&&&&&&&&&&&&&&&&&&&&&&&&&4566776788787",data)
					for i in data:
								
							sum_billable += i.get(billable) if i.get(billable) else 0

							sum_billable_f = "{:.2f}".format(sum_billable)
						
							sum_actual += i.get(actual) if i.get(actual) else 0

							sum_actual_f = "{:.2f}".format(sum_actual)
						
							sum_alloc += i.get(allocation) if i.get(allocation) else 0
							print(i.get(allocation))
							sum_alloc_f = "{:.2f}".format(sum_alloc)
							print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",sum_alloc_f)
						
							sum_wh += i.get(wh) if i.get(wh) else 0

							sum_wh_f = "{:.2f}".format(sum_wh)

							sum_rup += i.get(rup) if i.get(rup) else 0

							sum_rup_f = "{:.2f}".format(sum_rup/len(data))

							sum_avg_billable += i.get(avg_bill) if i.get(avg_bill) else 0

							sum_avg_billable_f = "{:.2f}".format((sum_avg_billable/float(sum_wh_f))*100) if float(sum_wh_f)  > 0 else 0

							avb = "{:.2f}".format((float(sum_avg_billable)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0

							tvb = "{:.2f}".format((float(sum_avg_billable)/float(sum_actual_f))*100) if float(sum_actual_f) > 0 else 0

							avw = "{:.2f}".format((float(sum_alloc_f)/float(sum_wh_f))*100) if float(sum_wh_f) > 0 else 0

							tva = "{:.2f}".format((float(sum_actual_f)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0


		
			return [
				{"label":"Total Working Hours","value":sum_wh_f,'indicator':'Red'},
				{"label":"Total Allocation","value": sum_alloc_f,'indicator':'Red'},
				{"label":"Total Timesheet Hours","value": sum_actual_f,'indicator':'Red'},
				{"label":"Total Billable Hours","value":sum_billable_f,'indicator':'Red'},
				{"label":"Allocation Vs Working %","value":avw,'indicator':'Red'},
				{"label":"Timesheet Vs Allocation %","value":tva,'indicator':'Red'},
				{"label":"Billable Vs Working %","value":sum_avg_billable_f,'indicator':'Red'},
				{"label":"Billable Vs Allocation %","value":avb,'indicator':'Red'},
				{"label":"Billable Vs Timesheet %","value":tvb,'indicator':'Red'}	
			]

		if filters.get("periodicity")=="Monthly":
			month_date_ranges = []
			start_date_str = filters.get("from_date")
			end_date_str = filters.get("to_date")

			start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
			end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

			# Create a while loop to iterate through the months
			current_date = start_date
			while current_date <= end_date:
				month_start = current_date.replace(day=1)
				if current_date.month == 12:
					next_month = current_date.replace(year=current_date.year + 1, month=1)
				else:
					next_month = current_date.replace(month=current_date.month + 1)
				month_end = (next_month - timedelta(days=1))
				
				month_date_ranges.append({
					"from_date": month_start.strftime("%Y-%m-%d"),
					"to_date": month_end.strftime("%Y-%m-%d")
				})
				
				current_date = next_month

			for month in month_date_ranges:				
				labels.append(str(month.get("from_date")) + "-" + str(month.get("to_date")))
				billable = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"
				actual = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_aw"
				allocation =str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_"+ 'alloc'
				wh = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_wh"
				rup = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_rup"
				avg_bill = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"

				if data:
						for i in data:
							
							sum_billable += i.get(billable) if i.get(billable) else 0

							sum_billable_f = "{:.2f}".format(sum_billable)
						
							sum_actual += i.get(actual) if i.get(actual) else 0

							sum_actual_f = "{:.2f}".format(sum_actual)
						
							sum_alloc += i.get(allocation) if i.get(allocation) else 0

							sum_alloc_f = "{:.2f}".format(sum_alloc)
						
							sum_wh += i.get(wh) if i.get(wh) else 0

							sum_wh_f = "{:.2f}".format(sum_wh)

							sum_rup += i.get(rup) if i.get(rup) else 0

							sum_rup_f = "{:.2f}".format(sum_rup/len(data))

							sum_avg_billable += i.get(avg_bill) if i.get(avg_bill) else 0
							print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", i.get(avg_bill))
							sum_avg_billable_f = "{:.2f}".format((sum_avg_billable/float(sum_wh_f))*100) if float(sum_wh_f)  > 0 else 0
							

							avb = "{:.2f}".format((float(sum_avg_billable)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0

							tvb = "{:.2f}".format((float(sum_avg_billable)/float(sum_actual_f))*100) if float(sum_actual_f) > 0 else 0

							avw = "{:.2f}".format((float(sum_alloc_f)/float(sum_wh_f))*100) if float(sum_wh_f) > 0 else 0

							tva = "{:.2f}".format((float(sum_actual_f)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0


		
			return [
				{"label":"Total Working Hours","value":sum_wh_f,'indicator':'Red'},
				{"label":"Total Allocation","value": sum_alloc_f,'indicator':'Red'},
				{"label":"Total Timesheet Hours","value": sum_actual_f,'indicator':'Red'},
				{"label":"Total Billable Hours","value":sum_billable_f,'indicator':'Red'},
				{"label":"Allocation Vs Working %","value":avw,'indicator':'Red'},
				{"label":"Timesheet Vs Allocation %","value":tva,'indicator':'Red'},
				{"label":"Billable Vs Working %","value":sum_avg_billable_f,'indicator':'Red'},
				{"label":"Billable Vs Allocation %","value":avb,'indicator':'Red'},
				{"label":"Billable Vs Timesheet %","value":tvb,'indicator':'Red'}	
			]
		if filters.get("periodicity")=="Fortnightly":
			month_date_ranges = []
			# current_date = datetime.datetime.strptime(filters.get("from_date"), "%Y-%m-%d")

			# while current_date <= datetime.datetime.strptime(filters.get("to_date"), "%Y-%m-%d"):
			# 	print("current_date", current_date)
				
			# 	last_day_of_month = (current_date + relativedelta(day=31)).replace(day=1) - datetime.timedelta(days=1)
			# 	to_date = min(last_day_of_month, current_date + datetime.timedelta(days=6))
				
			# 	month_date_ranges.append({
			# 		"from_date": current_date.strftime("%Y-%m-%d"),
			# 		"to_date": to_date.strftime("%Y-%m-%d")
			# 	})
				
			# 	current_date += relativedelta(months=1)
			interval = timedelta(days=14)

			# Initialize a list to store the date ranges
			start_date=getdate(filters.get("from_date"))
			end_date=getdate(filters.get("to_date"))
			# Start from the first date and keep adding the interval until you reach the end date
			while start_date <= end_date:
				# Calculate the end date for the current range
				end_of_fortnight = start_date + interval - timedelta(days=1)
				
				# Ensure the end date does not exceed the end_date
				if end_of_fortnight > end_date:
					end_of_fortnight = end_date
				
				# Add the current date range to the list
				month_date_ranges.append({
					"from_date": start_date.strftime("%Y-%m-%d"),
					"to_date": end_of_fortnight.strftime("%Y-%m-%d")
				})
				
				# Move to the next fortnight
				start_date = end_of_fortnight + timedelta(days=1)

			print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$67767887878",month_date_ranges)
			for month in month_date_ranges:				
				labels.append(str(month.get("from_date")) + "-" + str(month.get("to_date")))
				billable = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"
				actual = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_aw"
				allocation =str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_"+ 'alloc'
				wh = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_wh"
				rup = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_rup"
				avg_bill = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"

				if data:
						for i in data:
							
							sum_billable += i.get(billable) if i.get(billable) else 0

							sum_billable_f = "{:.2f}".format(sum_billable)
						
							sum_actual += i.get(actual) if i.get(actual) else 0

							sum_actual_f = "{:.2f}".format(sum_actual)
						
							sum_alloc += i.get(allocation) if i.get(allocation) else 0

							sum_alloc_f = "{:.2f}".format(sum_alloc)
						
							sum_wh += i.get(wh) if i.get(wh) else 0

							sum_wh_f = "{:.2f}".format(sum_wh)

							sum_rup += i.get(rup) if i.get(rup) else 0

							sum_rup_f = "{:.2f}".format(sum_rup/len(data))

							sum_avg_billable += i.get(avg_bill) if i.get(avg_bill) else 0

							sum_avg_billable_f = "{:.2f}".format((sum_avg_billable/float(sum_wh_f))*100) if float(sum_wh_f)  > 0 else 0

							avb = "{:.2f}".format((float(sum_avg_billable)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0

							tvb = "{:.2f}".format((float(sum_avg_billable)/float(sum_actual_f))*100) if float(sum_actual_f) > 0 else 0

							avw = "{:.2f}".format((float(sum_alloc_f)/float(sum_wh_f))*100) if float(sum_wh_f) > 0 else 0

							tva = "{:.2f}".format((float(sum_actual_f)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0


		
			return [
				{"label":"Total Working Hours","value":sum_wh_f,'indicator':'Red'},
				{"label":"Total Allocation","value": sum_alloc_f,'indicator':'Red'},
				{"label":"Total Timesheet Hours","value": sum_actual_f,'indicator':'Red'},
				{"label":"Total Billable Hours","value":sum_billable_f,'indicator':'Red'},
				{"label":"Allocation Vs Working %","value":avw,'indicator':'Red'},
				{"label":"Timesheet Vs Allocation %","value":tva,'indicator':'Red'},
				{"label":"Billable Vs Working %","value":sum_avg_billable_f,'indicator':'Red'},
				{"label":"Billable Vs Allocation %","value":avb,'indicator':'Red'},
				{"label":"Billable Vs Timesheet %","value":tvb,'indicator':'Red'}	
			]
		
		
		if filters.get("periodicity") == "Yearly":
			year_date_ranges = []
			from_date= getdate(filters.get("from_date"))
			to_date= getdate(filters.get("to_date"))

			# from_date = datetime.datetime.strptime(from_date_str, "%d-%m-%Y")
			# to_date = datetime.datetime.strptime(to_date_str, "%d-%m-%Y")

			# yearly_dates = []

			while from_date.year <= to_date.year:
				start_date = from_date.replace(month=1, day=1)
				end_date = from_date.replace(month=12, day=31)
				
				if from_date.year == to_date.year:
					end_date = to_date
				
				year_date_ranges.append({"from_date": start_date.strftime("%d-%m-%Y"), "to_date": end_date.strftime("%d-%m-%Y")})
				
				from_date = from_date.replace(year=from_date.year + 1)

			labels = []
			sum_alloc = 0.0
			sum_billable = 0.0
			sum_actual = 0.0
			sum_wh = 0.0
			sum_rup = 0.0
			sum_avg_billable = 0.0

			for month in year_date_ranges:
				labels.append(str(month.get("from_date")) + "-" + str(month.get("to_date")))
				billable = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"
				actual = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_aw"
				allocation =str(month.get("from_date"))+"-"+str(month.get("to_date"))+"_"+ 'alloc'
				wh = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_wh"
				rup = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_rup"
				avg_bill = str(month.get("from_date")) + "-" + str(month.get("to_date")) + "_bw"

				if data:
					for i in data:
								
							sum_billable += i.get(billable) if i.get(billable) else 0

							sum_billable_f = "{:.2f}".format(sum_billable)
						
							sum_actual += i.get(actual) if i.get(actual) else 0

							sum_actual_f = "{:.2f}".format(sum_actual)
						
							sum_alloc += i.get(allocation) if i.get(allocation) else 0

							sum_alloc_f = "{:.2f}".format(sum_alloc)
						
							sum_wh += i.get(wh) if i.get(wh) else 0

							sum_wh_f = "{:.2f}".format(sum_wh)

							sum_rup += i.get(rup) if i.get(rup) else 0

							sum_rup_f = "{:.2f}".format(sum_rup/len(data))

							sum_avg_billable += i.get(avg_bill) if i.get(avg_bill) else 0

							sum_avg_billable_f = "{:.2f}".format((sum_avg_billable/float(sum_wh_f))*100) if float(sum_wh_f)  > 0 else 0

							avb = "{:.2f}".format((float(sum_avg_billable)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0

							tvb = "{:.2f}".format((float(sum_avg_billable)/float(sum_actual_f))*100) if float(sum_actual_f) > 0 else 0

							avw = "{:.2f}".format((float(sum_alloc_f)/float(sum_wh_f))*100) if float(sum_wh_f) > 0 else 0

							tva = "{:.2f}".format((float(sum_actual_f)/float(sum_alloc_f))*100) if float(sum_alloc_f) > 0 else 0


		
			return [
				{"label":"Total Working Hours","value":sum_wh_f,'indicator':'Red'},
				{"label":"Total Allocation","value": sum_alloc_f,'indicator':'Red'},
				{"label":"Total Timesheet Hours","value": sum_actual_f,'indicator':'Red'},
				{"label":"Total Billable Hours","value":sum_billable_f,'indicator':'Red'},
				{"label":"Allocation Vs Working %","value":avw,'indicator':'Red'},
				{"label":"Timesheet Vs Allocation %","value":tva,'indicator':'Red'},
				{"label":"Billable Vs Working %","value":sum_avg_billable_f,'indicator':'Red'},
				{"label":"Billable Vs Allocation %","value":avb,'indicator':'Red'},
				{"label":"Billable Vs Timesheet %","value":tvb,'indicator':'Red'}	
			]


