# # Copyright (c) 2013, Dexciss and contributors
# # For license information, please see license.txt

import frappe
from frappe import _
from datetime import date, timedelta, datetime
from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange
from frappe.utils import (
	add_days,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	getdate,
	nowdate,
)
#
# def execute(filters=None):
# 	# columns, data = [], []
# 	condition = get_condition(filters)
# 	columns = get_columns(filters)
# 	data = get_data(filters,condition)
# 	return columns, data
#
# def get_columns(filters):
#
# 	columns = [
# 		{
# 			"label": _("Resource"),
# 			"fieldtype": "Link",
# 			"fieldname": "resource",
# 			"options": "Employee",
# 			"width": 140
# 		}
# 	]
# 	for dt in daterange(getdate(filters.from_date), getdate(filters.to_date)):
# 		columns.append(
# 			{
# 				"label": _(dt),
# 				"fieldtype": "Data",
# 				"fieldname": str(dt),
# 				"width": 140
# 			}
# 	)
# 	return columns
#
# def get_data(filters,condition):
# 	data = []
# 	for dt in daterange(getdate(filters.from_date), getdate(filters.to_date)):
# 		query = """ select tm.employee_name as resource ,
# 					case when td.is_billable = 1 then td.billing_hours
# 						else td.hours  end as '{0}'
# 					from `tabTimesheet` tm , `tabTimesheet Detail` td, `tabProject` p
# 					where tm.name = td.parent and td.project = p.name
# 					 and tm.start_date = '{2}'
# 					{1} """.format(dt,condition,dt)
#
# 		print("query------------------------",query)
# 		res = frappe.db.sql(query,as_dict=1)
# 		# print("res--------------------",res)
# 		for d in res:
# 			data.append(d)
# 	return data
#
# def get_condition(filters):
# 	query = """ and tm.docstatus = 1 """
# 	if filters.billable:
# 		query += """ and td.is_billable = 1 """
# 	if filters.project:
# 		query += """ and  td.project = '{0}' """.format(filters.project)
# 	if filters.employee:
# 		query += """ and tm.employee = '{0}' """.format(filters.employee)
# 	if filters.department:
# 		query += """ and  p.department = '{0}' """.format(filters.department)
# 	return query

def execute(filters=None):
	if not filters: filters ={}
	data = []
	conditions = get_columns(filters)
	data = get_data(filters, conditions)
	return conditions["columns"], data

def get_columns(filters):
	validate_filters(filters)

	# get conditions for based_on filter cond
	based_on_details = based_wise_columns_query(filters.get("based_on"))
	# get conditions for periodic filter cond
	period_cols, period_select = period_wise_columns_query(filters)
	# get conditions for grouping filter cond
	group_by_cols = group_wise_column(filters.get("group_by"))

	columns = based_on_details["based_on_cols"] + period_cols + [_("Total(Hrs)") + ":Float:120"]
	if group_by_cols:
		columns = based_on_details["based_on_cols"] + group_by_cols + period_cols + \
			[_("Total(Hrs)") + ":Float:120"]
		# print(columns)

	conditions = {"based_on_select": based_on_details["based_on_select"], "period_wise_select": period_select,
		"columns": columns, "group_by": based_on_details["based_on_group_by"], "grbc": group_by_cols,
		"addl_tables": based_on_details["addl_tables"], "addl_tables_relational_cond": based_on_details.get("addl_tables_relational_cond", "")}

	return conditions

def validate_filters(filters):
	for f in ["Fiscal Year", "Based On", "Period", "Company"]:
		if not filters.get(f.lower().replace(" ", "_")):
			frappe.throw(_("{0} is mandatory").format(f))

	if not frappe.db.exists("Fiscal Year", filters.get("fiscal_year")):
		frappe.throw(_("Fiscal Year {0} Does Not Exist").format(filters.get("fiscal_year")))

	if filters.get("based_on") == filters.get("group_by"):
		frappe.throw(_("'Based On' and 'Group By' can not be same"))

def based_wise_columns_query(based_on):
	based_on_details = {}

	# based_on_cols, based_on_select, based_on_group_by, addl_tables
	if based_on == "Employee":
		based_on_details["based_on_cols"] = ["Employee:Link/Employee:120", "Employee Name:Data:120"]
		based_on_details["based_on_select"] = "t1.employee, t1.employee_name,"
		based_on_details["based_on_group_by"] = 't1.employee'
		based_on_details["addl_tables"] = ''


	elif based_on == "Project":
		based_on_details["based_on_cols"] = ["Project:Link/Project:120","Project Name:Data:120"]
		based_on_details["based_on_select"] = "t2.project, t2.project_name,"
		based_on_details["based_on_group_by"] = 't2.project'
		based_on_details["addl_tables"] = ''

	elif based_on == 'Department':
		based_on_details["based_on_cols"] = ["Department:Link/Department:140"]
		based_on_details["based_on_select"] = "t3.department,"
		based_on_details["based_on_group_by"] = 't3.department'
		based_on_details["addl_tables"] = ',`tabProject` t3'
		based_on_details["addl_tables_relational_cond"] = " and t2.project = t3.name"

	elif based_on == 'Employee Group':
		based_on_details["based_on_cols"] = ["Employee Group:Link/Employee Group:140"]
		based_on_details["based_on_select"] = "t3.employee_group,"
		based_on_details["based_on_group_by"] = 't3.employee_group'
		based_on_details["addl_tables"] = ',`tabTask` t3'
		based_on_details["addl_tables_relational_cond"] = " and t2.task = t3.name"

	return based_on_details

def period_wise_columns_query(filters):
	query_details = ''
	pwc = []
	# bet_dates = get_period_date_ranges(filters.get("period"), filters.get("fiscal_year"))
	bet_dates = get_period_date_ranges(filters, filters.get("fiscal_year"))
	trans_date = 'start_date'

	if filters.get("period") == 'Yearly':
		pwc = [_(filters.get("fiscal_year")) + " ("+_("Hrs") + "):Float:120"]
		query_details = " SUM(t2.hours),"
		# for dt in bet_dates:
		# 	get_period_wise_columns(dt, filters.get("period"), pwc)
		# 	query_details = get_period_wise_query(dt, trans_date, query_details)
	elif filters.get("period") == 'Daily':
		for dt in bet_dates:
			pwc+=[dt[0]+":Float:120"]
			query_details = get_day_wise_query(dt,trans_date,query_details)
			print(query_details)
	else:
		for dt in bet_dates:
			get_period_wise_columns(dt, filters.get("period"), pwc)
			query_details = get_period_wise_query(dt, trans_date, query_details)
		# pwc = [_(filters.get("fiscal_year")) + " ("+_("Hrs") + "):Float:120"]
		# query_details = " SUM(t2.hours),"

	query_details += 'SUM(t2.hours)'
	return pwc, query_details


@frappe.whitelist(allow_guest=True)
def get_period_date_ranges(filters, fiscal_year=None, year_start_date=None):
	period = filters.get("period")
	from dateutil.relativedelta import relativedelta

	if not year_start_date:
		year_start_date, year_end_date = frappe.db.get_value("Fiscal Year",
			fiscal_year, ["year_start_date", "year_end_date"])

	period_date_ranges = []
	if period == "Daily":
		from_date = datetime.strptime(filters.get("from_date"),"%Y-%m-%d").strftime("%Y,%m,%d")
		to_date = datetime.strptime(filters.get("to_date"),"%Y-%m-%d").strftime("%Y,%m,%d")
		start_dt = datetime.strptime(from_date,"%Y,%m,%d").date()
		end_dt = datetime.strptime(to_date,"%Y,%m,%d").date()
		for dt in daterange_find(start_dt, end_dt):
			period_date_ranges.append([dt.strftime("%Y-%m-%d")])
	else:
		increment = {
			"Monthly": 1,

		}.get(period)
		for i in range(1, 13, increment):
			period_end_date = getdate(year_start_date) + relativedelta(months=increment, days=-1)
			if period_end_date > getdate(year_end_date):
				period_end_date = year_end_date
			period_date_ranges.append([year_start_date, period_end_date])
			year_start_date = period_end_date + relativedelta(days=1)
			if period_end_date == year_end_date:
				break
	
	return period_date_ranges

def daterange_find(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def get_mon(dt):
	return getdate(dt).strftime("%b")

def get_period_wise_columns(bet_dates, period, pwc):
	if period == 'Monthly':
		pwc += [_(get_mon(bet_dates[0])) + " (" + _("Hrs") + "):Float:120"]
	else:
		pwc += [_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Hrs") + "):Float:120"]

def get_period_wise_query(bet_dates, trans_date, query_details):
	query_details += """SUM(IF(t1.%(trans_date)s BETWEEN '%(sd)s' AND '%(ed)s', t2.hours, NULL)),
				""" % {"trans_date": trans_date, "sd": bet_dates[0],"ed": bet_dates[1]}
	return query_details

def get_day_wise_query(bet_dates,trans_date,query_details):
	print(bet_dates,trans_date,query_details)
	query_details += """SUM(IF(t1.%(trans_date)s='%(sd)s',t2.hours,NULL)),
				""" %{"trans_date": trans_date, "sd": bet_dates[0]}
	return query_details

def group_wise_column(group_by):
	if group_by:
		# return [group_by+":Link/"+group_by+":120"]
		return [group_by+":Link/"+group_by+":120",group_by+" Name"+":Data/"+group_by+" Name:120"]
	else:
		return []



def get_data(filters, conditions):
	data = []
	inc, cond= '',''
	query_details =  conditions["based_on_select"] + conditions["period_wise_select"]

	posting_date = 't1.start_date'

	if conditions["based_on_select"] in ["t1.project,", "t2.project,"]:
		cond = ' and '+ conditions["based_on_select"][:-1] +' IS Not NULL'

	if filters.project:
		cond += " and t2.project = '{0}' ".format(filters.project)
	if filters.employee:
		cond += "and t1.employee = '{}' ".format(filters.employee)
	if filters.billable:
		cond += "and t2.is_billable = 1"

	if(filters.get("period")=="Daily"):
		year_start_date,year_end_date = filters.get("from_date"),filters.get("to_date")
	else:
		year_start_date, year_end_date = frappe.db.get_value("Fiscal Year",
		filters.get('fiscal_year'), ["year_start_date", "year_end_date"])
	# year_start_date, year_end_date = frappe.db.get_value("Fiscal Year",
	# 	filters.get('fiscal_year'), ["year_start_date", "year_end_date"])

	if filters.get("group_by"):
		sel_col = ''
		sel_col1 = ''
		ind = conditions["columns"].index(conditions["grbc"][0])

		if filters.get("group_by") == 'Employee':
			sel_col = 't1.employee'
			sel_col1 = 't1.employee_name'
		elif filters.get("group_by") == 'Project':
			sel_col = 't2.project'
			sel_col1 = 't2.project_name'

		if filters.get('based_on') in ['Employee','Project']:
			inc = 2
		else :
			inc = 1 #priviously 1

		data1 = frappe.db.sql(""" select %s from `tab%s` t1, `tab%s Detail` t2 %s
					where t2.parent = t1.name and t1.company = %s and %s between %s and %s and
					t1.docstatus = 1 and t1.status!="Cancelled" %s %s
					group by %s
				""" % (query_details, "Timesheet", "Timesheet", conditions["addl_tables"], "%s",
					posting_date, "%s", "%s", conditions.get("addl_tables_relational_cond"), cond, conditions["group_by"]), (filters.get("company"),
					year_start_date, year_end_date),as_list=1)
		for d in range(len(data1)):
			#to add blanck column
			print("d123456789",d)
			dt = data1[d]
			print("data1[",data1[d])
			dt.insert(ind,'')
			# print("ind123456789",ind)
			dt.insert(ind+1,'')
			print("ind123456789",ind+1)
			for items in data1:
				print("items1234556",items)



			print("dt123456789",dt)

			data.append(dt)

			#to get distinct value of col specified by group_by in filter
			row = frappe.db.sql("""select DISTINCT(%s),%s  from `tab%s` t1, `tab%s Detail` t2 %s
						where t2.parent = t1.name and t1.company = %s and %s between %s and %s
						and t1.docstatus = 1 and t1.status!="Cancelled" and %s = %s %s %s
					""" %
					(sel_col,sel_col1,  "Timesheet",  "Timesheet", conditions["addl_tables"],
						"%s", posting_date, "%s", "%s", conditions["group_by"], "%s", conditions.get("addl_tables_relational_cond"), cond),
					(filters.get("company"), year_start_date, year_end_date, data1[d][0]), as_list=1)
			for i in range(len(row)):
				des = ['' for q in range(len(conditions["columns"]))]

				#get data for group_by filter
				row1 = frappe.db.sql(""" select %s , %s , %s from `tab%s` t1, `tab%s Detail` t2 %s
							where t2.parent = t1.name and t1.company = %s and %s between %s and %s
							and t1.docstatus = 1 and t1.status!="Cancelled" and %s = %s and %s = %s %s %s
						""" %
						(sel_col,sel_col1, conditions["period_wise_select"], "Timesheet",
							"Timesheet", conditions["addl_tables"], "%s", posting_date, "%s","%s", sel_col,
							"%s", conditions["group_by"], "%s", conditions.get("addl_tables_relational_cond"), cond),
						(filters.get("company"), year_start_date, year_end_date, row[i][0],
							data1[d][0]), as_list=1)
				des[ind] = row[i][0]
				des[ind+1] = row[i][1]
				for j in range(2,len(conditions["columns"])-inc):
					des[j+inc] = row1[0][j]
					print("des1234567890",des)
				data.append(des)
	else:
		data = frappe.db.sql(""" select %s from `tab%s` t1, `tab%s Detail` t2 %s
					where t2.parent = t1.name and t1.company = %s and %s between %s and %s and
					t1.docstatus = 1 and t1.status!="Cancelled" %s %s
					group by %s
				""" %
				(query_details, "Timesheet", "Timesheet", conditions["addl_tables"],
					"%s", posting_date, "%s", "%s", cond, conditions.get("addl_tables_relational_cond", ""), conditions["group_by"]),
				(filters.get("company"), year_start_date, year_end_date), as_list=1)
		print(""" select %s from `tab%s` t1, `tab%s Detail` t2 %s
					where t2.parent = t1.name and t1.company = %s and %s between %s and %s and
					t1.docstatus = 1 and t1.status!="Cancelled" %s %s
					group by %s
				""" %
				(query_details, "Timesheet", "Timesheet", conditions["addl_tables"],
					"%s", posting_date, "%s", "%s", cond, conditions.get("addl_tables_relational_cond", ""), conditions["group_by"]),
				(filters.get("company"), year_start_date, year_end_date))

	return data