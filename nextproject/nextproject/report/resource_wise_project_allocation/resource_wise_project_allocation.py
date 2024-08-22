# Copyright (c) 2013, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from collections import defaultdict

from frappe.utils.data import flt


def execute(filters=None):
	condition = get_condition(filters)
	columns = get_columns(filters)
	data = get_data(filters,condition)
	return columns, data

def get_columns(filters):
	if not filters.project_wise_resource:
		columns = [
			{
				"label": _("Resource"),
				"fieldtype": "Link",
				"fieldname": "resource",
				"options": "Employee",
				"width": 140
			},
			
		]
		proj_list = frappe.db.sql(""" select distinct(td.project) as project, p.project_name
									from `tabTimesheet Detail` td, `tabProject` p where td.project = p.name and p.company = '{0}'""".format(filters.company), as_dict=1)
		for project in proj_list:
			if filters.show_open_projects:
				proj=frappe.get_doc("Project",project.project)
				if proj.status=="Open":
					if filters.project:
						if project.project == filters.project:
							columns.append(
								{
									"label": _(project.project+'( '+project.project_name+' )'),
									"fieldtype": "Float",
									"fieldname": str(project.project),
									"width": 190
								}
							)
					else:
						columns.append(
							{
								"label": _(project.project+'( '+project.project_name+' )')	,
								"fieldtype": "Float",
								"fieldname": str(project.project),
								"width": 190
							}
						)
			else:
				if filters.project:
					if project.project == filters.project:
						columns.append(
							{
								"label": _(project.project+'( '+project.project_name+' )'),
								"fieldtype": "Float",
								"fieldname": str(project.project),
								"width": 190
							}
						)
				else:
					columns.append(
						{
							"label": _(project.project+'( '+project.project_name+' )')	,
							"fieldtype": "Float",
							"fieldname": str(project.project),
							"width": 190
						}
					)
		columns.append({
				"label": _("Total"),
				"fieldtype": "Float",
				"fieldname": "total",
				"width": 140
			})
		return columns

	elif filters.project_wise_resource == 1:
		columns = [
			{
				"label": _("Project"),
				"fieldtype": "Link",
				"fieldname": "project",
				"options": "Project",
				"width": 140
			}
		]
		emp_list = frappe.db.sql(""" select distinct(tm.employee) as employee, tm.employee_name as employee_name
										from `tabTimesheet` tm where tm.docstatus = 1""", as_dict=1)
		for emp in emp_list:
			if filters.show_active:
				if emp.employee:
					employee=frappe.get_doc("Employee",emp.employee)
					if employee.status=="Active": #
						if filters.employee:
							if emp.employee == filters.employee:
								columns.append(
									{
										"label": _(emp.employee+emp.employee_name),
										"fieldtype": "Float",
										"fieldname": str(emp.employee),
										"width": 190
									}
								)
						else:
							columns.append(
								{
									"label": _(str(emp.employee)+'( '+str(emp.employee_name)+' )'),
									"fieldtype": "Float",
									"fieldname": str(emp.employee),
									"width": 190
								}
							)
			else:
				
				if filters.employee:
					if emp.employee == filters.employee:
						columns.append(
							{
								"label": _(emp.employee+emp.employee_name),
								"fieldtype": "Float",
								"fieldname": str(emp.employee),
								"width": 190
							}
						)
				else:
					columns.append(
						{
							"label": _(str(emp.employee)+'( '+str(emp.employee_name)+' )'), #
							"fieldtype": "Float",
							"fieldname": str(emp.employee),
							"width": 190
						}
				)
					
		columns.append({
				"label": _("Total"),
				"fieldtype": "Float",
				"fieldname": "total",
				"width": 140
			})
		return columns


def get_data(filters,condition):
	   
	if not filters.project_wise_resource:
		
		result = []
		data = defaultdict(lambda: defaultdict(float))

        # Fetch all distinct projects and corresponding data
		q1 = """SELECT tm.employee_name AS resource, tm.employee,
                    p.name AS project, 
                    SUM(CASE WHEN {0} THEN td.billing_hours ELSE td.hours END) AS hours
            FROM `tabTimesheet` tm
            INNER JOIN `tabTimesheet Detail` td ON tm.name = td.parent
            INNER JOIN `tabProject` p ON td.project = p.name
            WHERE tm.docstatus = 1 
			AND {1} AND p.company = '{2}'
            GROUP BY tm.employee, p.name""".format("1" if filters.billable == 1 else "0", condition, filters.company)
		
		res = frappe.db.sql(q1, as_dict=True)
		

		for d in res:
			if filters.show_active:
				employee = frappe.get_doc("Employee", d.employee)
				if employee.status == "Active":
					if filters.show_open_projects:
						proj = frappe.get_doc("Project", d['project'])
						if proj.status == "Open":
							data[d['employee']]['resource'] = d['resource']
							data[d['employee']][d['project']] = d['hours']
							data[d['employee']]['total'] += d['hours']
							
					else:
						data[d['employee']]['resource'] = d['resource']
						data[d['employee']][d['project']] = d['hours']
						data[d['employee']]['total'] += d['hours']
			else:
				if filters.show_open_projects:
					proj = frappe.get_doc("Project", d['project'])
					if proj.status == "Open":
						data[d['employee']]['resource'] = d['resource']
						data[d['employee']][d['project']] = d['hours']
						data[d['employee']]['total'] += d['hours']
								
				else:
					data[d['employee']]['resource'] = d['resource']
					data[d['employee']][d['project']] = d['hours']
					data[d['employee']]['total'] += d['hours']
		
        # Convert data to list
		result = list(data.values())
		return result

	elif filters.project_wise_resource == 1:
	
		result = []
		q1 = """
			SELECT p.name AS project, tm.employee,
				COALESCE(SUM(CASE WHEN {0} THEN td.billing_hours ELSE td.hours END), 0) AS hours
			FROM `tabTimesheet` tm
			LEFT JOIN `tabTimesheet Detail` td ON tm.name = td.parent
			LEFT JOIN `tabProject` p ON td.project = p.name
			WHERE tm.docstatus = 1 
				AND tm.employee IN (SELECT DISTINCT employee FROM `tabTimesheet` WHERE docstatus = 1)
				AND {1} and p.company = '{2}'
			GROUP BY tm.employee, td.project
		""".format("1" if filters.billable == 1 else "0", condition, filters.company)
        
		res = frappe.db.sql(q1, as_dict=1)

		grouped_data = defaultdict(dict)
		for d in res:
			if filters.show_active:
				employee = frappe.get_doc("Employee", d.employee)
				if employee.status == "Active":
					if filters.show_open_projects:
						proj = frappe.get_doc("Project", d.project)
						if proj.status == "Open":
							project = d['project']
							if project not in grouped_data:
								grouped_data[project] = {'project': project, 'total': 0}

							grouped_data[project].setdefault(d.employee, 0)
							grouped_data[project][d.employee] += flt(d.hours)
							grouped_data[project]['total'] += flt(d.hours)
					else:
						project = d['project']
						if project not in grouped_data:
							grouped_data[project] = {'project': project, 'total': 0}

						grouped_data[project].setdefault(d.employee, 0)
						grouped_data[project][d.employee] += flt(d.hours)
						grouped_data[project]['total'] += flt(d.hours)
			else:
				if filters.show_open_projects:
					proj = frappe.get_doc("Project", d.project)
					if proj.status == "Open":
						project = d['project']
						if project not in grouped_data:
							grouped_data[project] = {'project': project, 'total': 0}

						grouped_data[project].setdefault(d.employee, 0)
						grouped_data[project][d.employee] += flt(d.hours)
						grouped_data[project]['total'] += flt(d.hours)
				else:
					project = d['project']
					if project not in grouped_data:
						grouped_data[project] = {'project': project, 'total': 0}


					grouped_data[project].setdefault(d.employee, 0)
					grouped_data[project][d.employee] += flt(d.hours)
					grouped_data[project]['total'] += flt(d.hours)

		result = list(grouped_data.values())
		return result

def get_condition(filters):

	query =""

	if filters.from_date and filters.to_date:

		query+=" date(td.from_time) between '{0}' and '{1}' and date(td.to_time) between '{0}' and '{1}'".format(filters.from_date, filters.to_date)	

	if filters.billable:
		query += """ and td.is_billable = 1 """

	if filters.project:
		query += """ and  td.project = '{0}' """.format(filters.project)

	if filters.employee:
		query += """ and tm.employee = '{0}' """.format(filters.employee)

	if filters.department:
		query += """ and  p.department = '{0}' """.format(filters.department)

	return query
	
