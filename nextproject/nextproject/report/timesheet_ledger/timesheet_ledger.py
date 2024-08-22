# Copyright (c) 2022, Dexciss and contributors
# For license information, please see license.txt


from datetime import datetime
import frappe
from frappe.utils.data import flt




def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns,data,None


def get_columns(filters):
	

	columns = [
				
				{"fieldname":"task",
				"label": "Task",
				"fieldtype": "Link",
				"options" : "Task",
				"width":164},
				
				{"fieldname":"name",
				"label":"Timesheet_ID",
				"fieldtype":"Link",
				"options":"Timesheet",
				"width":140},

				{"fieldname":"expected_time",
				"label":"Expected Hours",
				"fieldtype":"Float"},

				{"fieldname":"consumed_hours",
				"label":"Consumed Hours",
				"fieldtype":"Float"},

				{"fieldname":"balance",
				"label":"Balance",
				"fieldtype":"Float"},

				{"fieldname":"from_time",
				"label": "Date",
				"fieldtype": "Date",
				"width":120},

				{"fieldname":"project",
				"label": "Project",
				"fieldtype": "Link",
				"options" : "Project"},

				{"fieldname":"project_name",
				"label": "Project Name",
				"fieldtype": "Data"},

				{"fieldname":"employee",
				"label":"Employee","fieldtype":"Link",
				"options":"Employee"},

				{"fieldname":"employee_name",
				"label":"Employee Name",
				"fieldtype":"Data"},
			
				{"fieldname":"description",
				"label":"Description",
				"fieldtype":"Small Text"}

			]
	
	return columns




def get_condition(filters):	
	conditions = ""

	if filters.get("company"):
		conditions += " And t.company ='%s'" % filters.get('company')

	if filters.get("from_time"):
		conditions += "AND DATE(ts.from_time)>='%s'" % filters.get('from_time')
	
	if filters.get("to_time"):
		conditions += " AND DATE(ts.to_time)<='%s'" % filters.get('to_time')

	if filters.get("project"):
		conditions += " And ts.project ='%s'" % filters.get('project')
	
	if filters.get("employee"):
		conditions += "And t.employee ='%s'" % filters.get('employee')
						
	if filters.get("task"):
		conditions += "And ts.task ='%s'" %filters.get('task')
							
	if filters.get("sales_invoice"):
		conditions += "And ts.sales_invoice='%s'" %filters.get('sales_invoice')
								
	if filters.get("is_billable"):
		conditions += "And ts.is_billable='%s'" %filters.get('is_billable')

	
	
	return conditions
										

def get_methods(filters):
	methods = ""

	if filters.get("project"):
		methods += " And ts.project ='%s'" % filters.get('project')

	if filters.get("employee"):
		methods += "And t.employee ='%s'" % filters.get('employee')
						
	if filters.get("task"):
		methods += "And ts.task ='%s'" %filters.get('task')
							
	if filters.get("sales_invoice"):
		methods += "And ts.sales_invoice='%s'" %filters.get('sales_invoice')
								
	if filters.get("is_billable"):
		methods += "And ts.is_billable='%s'" %filters.get('is_billable')

	return methods

def get_data(filters):
    methods = get_methods(filters)
    conditions = get_condition(filters)
    d = []
    closing = 0.0
    opening_balance = 0.0
    opening_consumed_hours = 0.0

    # Fetching opening balance and consumed hours
    tot = frappe.db.sql("""SELECT SUM(DISTINCT ta.expected_time) AS expected_time, SUM(ts.hours) AS consumed_hours
                           FROM `tabTimesheet` t
                           JOIN `tabTimesheet Detail` ts ON t.name = ts.parent 
                           JOIN `tabTask` ta ON ts.task = ta.name 
                           WHERE DATE(ts.from_time) < '{0}'{methods}
			   """.format(filters.get("from_time"), methods=methods), as_dict=1)
    
    for j in tot:
        j.update({"task": "Opening"})
        j.update({"balance": flt(j.get("expected_time")) - flt(j.get("consumed_hours"))})
        if j.get("task") == "Opening":
            closing += flt(j.get("expected_time"))
        d.append(j)
    opening_consumed_hours = flt(j.get("consumed_hours"))
    print("Opening Consuming Balance: ", opening_consumed_hours)

    s = frappe.db.sql("""SELECT DISTINCT(ts.task) AS task, ta.expected_time AS expected_time 
                        FROM `tabTimesheet` t
                        JOIN `tabTimesheet Detail` ts ON t.name = ts.parent 
                        JOIN `tabTask` ta ON ts.task = ta.name 
                        WHERE t.docstatus = 1{conditions}
                        ORDER BY ts.from_time ASC""".format(conditions=conditions), as_dict=1)

    for i in s:
        date = frappe.db.sql("""SELECT SUM(ts.hours) AS consumed_hours 
                               FROM `tabTimesheet Detail` ts 
                               WHERE ts.task = '{0}' AND DATE(ts.from_time) >= '{1}' 
                               AND docstatus = 1""".format(i.get("task"), filters.get("from_time")), as_dict=1)

        if date:
            i.update({"consumed_hours": date[0].get("consumed_hours"), "balance": flt(i.get("expected_time")) - flt(date[0].get("consumed_hours"))})
            d.append(i)

            data = frappe.db.sql("""SELECT ts.project, ta.expected_time AS exp, ts.hours AS consumed_hours, t.name AS name,
                                         ts.project_name, ts.from_time AS from_time, ts.project_name, ts.to_time AS to_time,
                                         t.employee, t.employee_name, ts.description, t.company
                                  FROM `tabTimesheet` t
                                  JOIN `tabTimesheet Detail` ts ON t.name = ts.parent 
                                  JOIN `tabTask` ta ON ts.task = ta.name 
                                  WHERE ts.docstatus = 1 AND ts.task = '{0}'{conditions}
                                  ORDER BY ts.from_time ASC """.format(i.get("task"), conditions=conditions), as_dict=1)

            exp_time = 0.0
            for o in data:
                expected_time = flt(o.get("exp"))
                from_date = filters.get("from_time")
                to_date = o.to_time
                consumed_hours = frappe.db.sql("""SELECT SUM(hours) AS consumed_hours 
                                                 FROM `tabTimesheet Detail` 
                                                 WHERE task = '{0}' AND 
                                                 DATE (from_time) >= '{1}' AND 
                                                 to_time <= '{2}' AND 
                                                 docstatus = 1
                                                 
						                            """.format(i.get("task"), from_date, to_date), as_dict=1)

                total_consumed_hours = consumed_hours[0]["consumed_hours"] if consumed_hours else 0
                expected_balance = expected_time - flt(total_consumed_hours)
                o.update({"balance": expected_balance})
                o.update({"expected_time": expected_balance + flt(o.get("consumed_hours"))})
                d.append(o)

    t = frappe.db.sql("""SELECT SUM(DISTINCT ta.expected_time) AS expected_time, SUM(ts.hours) AS consumed_hours 
                         FROM `tabTimesheet` t
                         JOIN `tabTimesheet Detail` ts ON t.name = ts.parent  
                         JOIN `tabTask` ta ON ts.task = ta.name 
                         WHERE ts.docstatus = 1 {conditions}
                         """.format(conditions=conditions), as_dict=1)
    for k in t:
        k.update({"task": "Total"})
        k.update({"balance": flt(k.get("expected_time")) - flt(k.get("consumed_hours"))})
        if k.get("task") == "Total":
            closing += flt(k.get("expected_time"))
        d.append(k)

    # Calculate the closing balance
    closing_consumed_hours = opening_consumed_hours + flt(k.get("consumed_hours"))
    closing_balance = {
        "task": "Closing(Open+Total)",
        "expected_time": closing,
        "consumed_hours": closing_consumed_hours,
        "balance": flt(closing) - flt(closing_consumed_hours)
    }
    d.append(closing_balance)

    return d
