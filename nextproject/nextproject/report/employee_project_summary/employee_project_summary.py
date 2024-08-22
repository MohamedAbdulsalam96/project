# Copyright (c) 2022, Dexciss and contributors
# For license information, please see license.txt


import frappe

def execute(filters=None):
	c = get_columns(filters)
	# gpby = group_by(filters)
	columns, data = c["columns"], get_data(c,filters)
	chart = get_chart_data(data,filters)
	report_summary = get_report_summary(filters,data)
	return columns, data , None , chart , report_summary

def get_columns(filters):
	

	
	based_on_details = based_wise_columns_query(filters.get("based_on"),filters)
	
	group_by_cols = group_wise_columns(filters.get("group_by"))
	static_cols = static_columns(filters)

	columns = based_on_details["based_on_cols"] + static_cols
	if group_by_cols:
		columns = based_on_details["based_on_cols"] + group_by_cols + static_cols
	
	conditions = {
		"columns": columns
		}
	
	print("********************",columns)

	return conditions





def based_wise_columns_query(based_on , filters):
	if filters.get("include_issues") == 1:
		
		based_on_details = {}

		if based_on == "Team Lead" and filters.get("group_by") == "Project":
			based_on_details["based_on_group_by"] = 'p.project_lead'
			based_on_details["based_on_cols"] = [{
					"label": ("Team Lead"),
					"fieldname": 'project_lead',
					"fieldtype": "Link",
					"options": "Employee",
					"width": 300
				},
				{
					"label": ("Team Lead Name"),
					"fieldname": 'project_lead_name',
					"fieldtype": "Data",
					"width": 300
				},
				]
			

		elif based_on == "Primary Consultant" and filters.get("group_by") == "Project":

			print("pc,proj,ii")
			based_on_details["based_on_group_by"] = 'p.primary_consultant'
			based_on_details["based_on_select"] = """p.primary_consultant,
													p.primary_consultant_name,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.primary_consultant = p.primary_consultant) + (select count(i.name) from `tabIssue` i where i.project = p.name and i.primary_consultant = p.primary_consultant)) as assigned,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.primary_consultant = p.primary_consultant and tk.status = "Completed")+(select count(i.name) from `tabIssue` i where i.project = p.name and i.primary_consultant = p.primary_consultant and i.status = "Closed" and i.status = "Resolved")) as completed,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.primary_consultant = p.primary_consultant and tk.status = "Overdue")+(select count(i.name) from `tabIssue` i where i.project = p.name and i.primary_consultant = p.primary_consultant and i.status = "Open")) as overdue,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.primary_consultant = p.primary_consultant and tk.status in ("Working","Pending Review","Open"))+(select count(i.name) from `tabIssue` i where i.project = p.name and i.primary_consultant = p.primary_consultant and i.status = "Open")) as working"""
			based_on_details["based_on_cols"] = [{
					"label": ("Primary Consultant"),
					"fieldname": 'primary_consultant',
					"fieldtype": "Link",
					"options": "Employee",
					"width": 300
				},
				{
					"label": ("Primary Consultant Name"),
					"fieldname": 'primary_consultant_name',
					"fieldtype": "Data",
					# "options": "Sales Person",
					"width": 300
				}]
			
			
			
			# based_on_details["addl_tables"] = ''

		elif based_on == "Department" and filters.get("group_by") == "Project":
			print("dpt,proj,ii")
			based_on_details["based_on_cols"] = ["Department:Link/Department:120"]
			based_on_details["based_on_group_by"] = 'p.department'
			based_on_details["addl_tables"] = ''

		elif based_on == "Employee Group" and filters.get("group_by") == "Project":
			print("eg,proj,ii")
			based_on_details["based_on_cols"] = ["Employee Group:Link/Employee Group"]
			based_on_details["based_on_select"] = """p.employee_group,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.employee_group = p.employee_group)+(select count(i.name) from `tabIssue` i where i.project = p.name and i.employee_group = p.employee_group)) as assigned,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.employee_group = p.employee_group and tk.status = "Completed")+(select count(i.name) from `tabIssue` i where i.project = p.name and i.employee_group = p.employee_group and i.status = "Closed" and i.status = "Resolved")) as completed,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.employee_group = p.employee_group and tk.status = "Overdue")+(select count(i.name) from `tabIssue` i where i.project = p.name and i.employee_group = p.employee_group and i.status = "Open")) as overdue,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.employee_group = p.employee_group and tk.status in ("Working","Pending Review","Open"))+(select count(i.name) from `tabIssue` i where i.project = p.name and i.employee_group = p.employee_group and i.status = "Open")) as working
													"""
			based_on_details["based_on_group_by"] = 'p.employee_group'
			based_on_details["addl_tables"] = ''
		
		elif based_on == "Team Lead" and  not filters.get("group_by"):
			print("tl,"",ii")

			# based_on_details["based_on_cols"] = ["Project Lead:Link/Employee:120", "Group Lead Name:Data:120"]
			based_on_details["based_on_select"] = """p.project_lead,
													p.project_lead_name,
													((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead) + (select count(tk.name) from `tabIssue` tk where  tk.project_lead = p.project_lead)) as assigned,
													((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Completed") + (select count(i.name) from `tabIssue` i where  i.project_lead = p.project_lead and i.status = "Closed" and i.status = "Resolved")) as completed,
													((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue") + (select count(i.name) from `tabIssue` i where   i.project_lead = p.project_lead and i.status = "Open")) as overdue,
													((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status in ("Working","Pending Review","Open")) + (select count(i.name) from `tabIssue` i where  i.project_lead = p.project_lead and i.status = "Open")) as working
													"""
			based_on_details["based_on_group_by"] = 'p.project_lead'
			# based_on_details["addl_tables"] = ''
			based_on_details["based_on_cols"] = [{
					"label": ("Team Lead"),
					"fieldname": 'project_lead',
					"fieldtype": "Link",
					"options": "Employee",
					"width": 300
				},
				{
					"label": ("Team Lead Name"),
					"fieldname": 'project_lead_name',
					"fieldtype": "Data",
					# "options": "Sales Person",
					"width": 300
				},
				]
			

		elif based_on == "Primary Consultant" and not filters.get("group_by"):
			print("pc,"",ii")
			based_on_details["based_on_group_by"] = 'p.primary_consultant'
			based_on_details["based_on_select"] = """p.primary_consultant,
													p.primary_consultant_name,
													((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant)+(select count(i.name) from `tabIssue` i where i.primary_consultant = p.primary_consultant)) as assigned,
													((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Completed")+(select count(i.name) from `tabIssue` i where i.primary_consultant = p.primary_consultant and i.status = "Closed"  or  i.status = "Resolved")) as completed,
													((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Overdue")+(select count(i.name) from `tabIssue` i where i.primary_consultant = p.primary_consultant and i.status = "Open")) as overdue,
													((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status in ("Working","Pending Review","Open"))+(select count(i.name) from `tabIssue` i where i.primary_consultant = p.primary_consultant and i.status = "Open")) as working"""
			based_on_details["based_on_cols"] = [{
					"label": ("Primary Consultant"),
					"fieldname": 'primary_consultant',
					"fieldtype": "Link",
					"options": "Employee",
					"width": 300
				},
				{
					"label": ("Primary Consultant Name"),
					"fieldname": 'primary_consultant_name',
					"fieldtype": "Data",
					# "options": "Sales Person",
					"width": 300
				}]
			
			
			
			# based_on_details["addl_tables"] = ''

		elif based_on == "Department" and not filters.get("group_by"):
			print("dpt,"",ii")
			based_on_details["based_on_cols"] = [{
					"label": ("Department"),
					"fieldname": 'department',
					"fieldtype": "Link",
					"options": "Department",
					"width": 300
				}]
			based_on_details["based_on_select"] = """p.department,
													((select count(tk.name) from `tabTask` tk where  tk.department = p.department)+(select count(i.name) from `tabIssue` i where  i.department_ = p.department)) as assigned,
													((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Completed")+(select count(i.name) from `tabIssue` i where  i.department_ = p.department and i.status = "Closed" or i.status = "Resolved")) as completed,
													((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Overdue")+(select count(i.name) from `tabIssue` i where i.department_ = p.department and i.status = "Open")) as overdue,
													((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status in ("Working","Pending Review","Open"))+(select count(i.name) from `tabIssue` i where  i.department_ = p.department and i.status = "Open")) as working"""
			based_on_details["based_on_group_by"] = 'p.department'
			based_on_details["addl_tables"] = ''

		elif based_on == "Employee Group" and not filters.get("group_by"):
			print("eg,"",ii")
			based_on_details["based_on_cols"] = ["Employee Group:Link/Employee Group"]
			based_on_details["based_on_select"] = """p.employee_group,
													((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group)+(select count(i.name) from `tabIssue` i where  i.employee_group = p.employee_group)) as assigned,
													((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status = "Completed")+(select count(i.name) from `tabIssue` i where  i.employee_group = p.employee_group and i.status = "Closed" and i.status = "Resolved")) as completed,
													((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status = "Overdue")+(select count(i.name) from `tabIssue` i where  i.employee_group = p.employee_group and i.status = "Open")) as overdue,
													((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status in ("Working","Pending Review","Open"))+(select count(i.name) from `tabIssue` i where i.employee_group = p.employee_group and i.status = "Open")) as working
													"""
			based_on_details["based_on_group_by"] = 'p.employee_group'
			based_on_details["addl_tables"] = ''


		return based_on_details

	elif filters.get("include_issues")== None:
		

		based_on_details = {}

		# based_on_cols, based_on_select, based_on_group_by, addl_tables
		if based_on == "Team Lead" and filters.get("group_by") == "Project":
			print("tl,proj,""")

			# based_on_details["based_on_cols"] = ["Project Lead:Link/Employee:120", "Group Lead Name:Data:120"]
			# based_on_details["based_on_select"] = """p.project_lead,
			# 										p.project_lead_name,
			# 										((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.project_lead = p.project_lead)) as assigned,
			# 										((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.project_lead = p.project_lead and tk.status = "Completed")) as completed,
			# 										((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.project_lead = p.project_lead and tk.status = "Overdue")) as overdue,
			# 										((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.project_lead = p.project_lead and tk.status in ("Working","Pending Review","Open"))) as working

			# 										"""
			based_on_details["based_on_group_by"] = 'p.project_lead'
			# based_on_details["addl_tables"] = ''
			based_on_details["based_on_cols"] = [{
					"label": ("Team Lead"),
					"fieldname": 'project_lead',
					"fieldtype": "Link",
					"options": "Employee",
					"width": 300
				},
				{
					"label": ("Team Lead Name"),
					"fieldname": 'project_lead_name',
					"fieldtype": "Data",
					# "options": "Sales Person",
					"width": 300
				},
				]
			

		elif based_on == "Primary Consultant" and filters.get("group_by") == "Project":
			print("pc,proj,""")
			# pct = frappe.db.sql("""
			# 						select distinct p.primary_consultant,p.primary_consultant_name  from `tabProject` p where p.is_active = "Yes" """,as_dict = 1)
			# for pc in pct:
			# 	print("pc,proj",pc)

			based_on_details["based_on_group_by"] = 'p.primary_consultant'
			based_on_details["based_on_select"] = """
													p.primary_consultant,
													p.primary_consultant_name,
													p.name as project,
													p.project_name as project_name,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.primary_consultant = p.primary_consultant)) as assigned,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.primary_consultant = p.primary_consultant and tk.status = "Completed")) as completed,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.primary_consultant = p.primary_consultant and tk.status = "Overdue")) as overdue,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.primary_consultant = p.primary_consultant and tk.status in ("Working","Pending Review","Open"))) as working"""
			based_on_details["based_on_cols"] = [{
					"label": ("Primary Consultant"),
					"fieldname": 'primary_consultant',
					"fieldtype": "Link",
					"options": "Employee",
					"width": 300
				},
				{
					"label": ("Primary Consultant Name"),
					"fieldname": 'primary_consultant_name',
					"fieldtype": "Data",
					# "options": "Sales Person",
					"width": 300
				}]
			
			
			
			# based_on_details["addl_tables"] = ''

		elif based_on == "Department" and filters.get("group_by") == "Project":
			print("dpt,proj,""")
			based_on_details["based_on_cols"] = ["Department:Link/Department:120"]
			based_on_details["based_on_select"] = """p.department,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.department = p.department)) as assigned,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.department = p.department and tk.status = "Completed")) as completed,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.department = p.department and tk.status = "Overdue")) as overdue,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.department = p.department and tk.status in ("Working","Pending Review","Open"))) as working"""
			based_on_details["based_on_group_by"] = 'p.department'
			based_on_details["addl_tables"] = ''

		elif based_on == "Employee Group" and filters.get("group_by") == "Project":
			print("eg,proj,""")
			based_on_details["based_on_cols"] = ["Employee Group:Link/Employee Group"]
			based_on_details["based_on_select"] = """p.employee_group,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.employee_group = p.employee_group)) as assigned,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.employee_group = p.employee_group and tk.status = "Completed")) as completed,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.employee_group = p.employee_group and tk.status = "Overdue")) as overdue,
													((select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.employee_group = p.employee_group and tk.status in ("Working","Pending Review","Open"))) as working
													"""
			based_on_details["based_on_group_by"] = 'p.employee_group'
			based_on_details["addl_tables"] = ''

		elif based_on == "Team Lead" and not filters.get("group_by"):
			print("tl,"",""")
			based_on_details["based_on_cols"] = [{
					"label": ("Team Lead"),
					"fieldname": 'project_lead',
					"fieldtype": "Link",
					"options": "Employee",
					"width": 300
				},
				{
					"label": ("Team Lead Name"),
					"fieldname": 'project_lead_name',
					"fieldtype": "Data",
					# "options": "Sales Person",
					"width": 300
				},
				]

			# based_on_details["based_on_cols"] = ["Project Lead:Link/Employee:120", "Group Lead Name:Data:120"]
			based_on_details["based_on_select"] = """p.project_lead,
													p.project_lead_name,
													((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead)) as assigned,
													((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Completed")) as completed,
													((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue")) as overdue,
													((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status in ("Working","Pending Review","Open"))) as working
													"""
			based_on_details["based_on_group_by"] = 'p.project_lead'
			# based_on_details["addl_tables"] = ''
			
			

		elif based_on == "Primary Consultant" and  not filters.get("group_by"):
			print("pc,"",""")
			based_on_details["based_on_group_by"] = 'p.primary_consultant'
			based_on_details["based_on_select"] = """p.primary_consultant,
													p.primary_consultant_name,
													((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant)) as assigned,
													((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Completed")) as completed,
													((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Overdue")) as overdue,
													((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status in ("Working","Pending Review","Open"))) as working"""
			based_on_details["based_on_cols"] = [{
					"label": ("Primary Consultant"),
					"fieldname": 'primary_consultant',
					"fieldtype": "Link",
					"options": "Employee",
					"width": 300
				},
				{
					"label": ("Primary Consultant Name"),
					"fieldname": 'primary_consultant_name',
					"fieldtype": "Data",
					# "options": "Sales Person",
					"width": 300
				}]
			
			
			
			# based_on_details["addl_tables"] = ''

		elif based_on == "Department" and not filters.get("group_by"):
			print("dpt,"",""")
			based_on_details["based_on_cols"] = ["Department:Link/Department:120"]
			# based_on_details["based_on_select"] = """p.department,
			# 										((select count(tk.name) from `tabTask` tk where  tk.department = p.department)) as assigned,
			# 										((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Completed")) as completed,
			# 										((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Overdue")) as overdue,
			# 										((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status in ("Working","Pending Review","Open"))) as working"""
			based_on_details["based_on_group_by"] = 'p.department'
			based_on_details["addl_tables"] = ''

		elif based_on == "Employee Group" and not filters.get("group_by"):
			print("eg,"",""")
			based_on_details["based_on_cols"] = ["Employee Group:Link/Employee Group"]
			based_on_details["based_on_select"] = """p.employee_group,
													((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group)) as assigned,
													((select count(tk.name) from `tabTask` tk where tk.employee_group = p.employee_group and tk.status = "Completed")) as completed,
													((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status = "Overdue")) as overdue,
													((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status in ("Working","Pending Review","Open"))) as working
													"""
			based_on_details["based_on_group_by"] = 'p.employee_group'
			based_on_details["addl_tables"] = ''

		
		print("**********dattttttttttttttttttttttttttttttt****************",based_on_details)

		return based_on_details



def group_wise_columns(group_by):
	if group_by == "Project":
		t_columns=[
			
			{
				"label": "Project",
				"fieldname": ("project"),
				"fieldtype": "Link",
				"options":"Project",
				"width": 200

			},
			{
				"label": "Project Name",
				"fieldname": ("project_name"),
				"fieldtype": "Data",
				"width": 200

			}
			]

		return t_columns




def static_columns(filters):
	t_columns =[]
	
	if filters.get("include_issues") == None:
		print("******************ifbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",filters.get("include_issues"))
		t_columns=[
			
			{
				"label": "Assigned Tasks",
				"fieldname": ("assigned"),
				"fieldtype": "Float",
				"width": 200

			},
			{
				"label": "Completed Tasks",
				"fieldname": ("completed"),
				"fieldtype": "Float",
				"width": 200

			},
			{
				"label": "Overdue Tasks",
				"fieldname": ("overdue"),
				"fieldtype": "Float",
				"width": 200

			},
			{
				"label": "Working Tasks",
				"fieldname": ("working"),
				"fieldtype": "Float",
				"width": 200

			},
			{
				"label": "Tasks Completion %",
				"fieldname": ("completion"),
				"fieldtype": "Percent",
				"width": 200

			},
			{
				"label": "Tasks Overdue% ",
				"fieldname": ("overdue_p"),
				"fieldtype": "Percent",
				"width": 200

			},
			{
				"fieldname": ("pending"),
				"label": "Tasks Pending%",
				"fieldtype": "Percent",
				"width": 200

			}
		]
	elif filters.get("include_issues") == 1:
		print("******************aaaaaaaaaaaaaaaaaaaaelse",filters.get("include_issues"))
		t_columns=[
			
			{
				"label": "Assigned (Tasks + Issues)",
				"fieldname": ("assigned"),
				"fieldtype": "Float",
				"width": 200

			},
			{
				"label": "Completed (Tasks + Issues)",
				"fieldname": ("completed"),
				"fieldtype": "Float",
				"width": 200

			},
			{
				"label": "Overdue Tasks",
				"fieldname": ("overdue"),
				"fieldtype": "Float",
				"width": 200

			},
			{
				"label": "Working Tasks",
				"fieldname": ("working"),
				"fieldtype": "Float",
				"width": 200

			},
			{
				"label": "(Tasks+Issues) Completion % ",
				"fieldname": ("completion"),
				"fieldtype": "Percent",
				"width": 200

			},
			{
				"label": "Tasks Overdue % ",
				"fieldname": ("overdue_p"),
				"fieldtype": "Percent",
				"width": 200

			},
			{
				"fieldname": ("pending"),
				"label": "(Tasks+Issues) Pending %",
				"fieldtype": "Percent",
				"width": 200

			}	
		]

	return t_columns

def get_data(conditions,filters):
	team_cond=[]
	if filters.get("team_lead"):
		team_lead_list = ", ".join([f"'{p.strip()}'" for p in filters.get("team_lead")])
		tl = " AND " +f" p.project_lead IN ({team_lead_list})"
	else:
		tl = ""

	primary_cond = []
	if filters.get("primary_consultant"):
		primary_consultant_list = ", ".join([f"'{p.strip()}'" for p in filters.get("primary_consultant")])
		pc = " AND " +f" p.primary_consultant IN ({primary_consultant_list})"
	else:
		pc = ""

	if filters.get("department"):
		dp = "AND p.department = '{0}'".format(filters.get("department"))
	else:
		dp = ""
	
	employee_cond=[]
	if filters.get("employee_group"):
		employee_list = ", ".join(["'{}'".format(p.replace("'", "\\'")) for p in filters.get("employee_group")])
		eg = "AND p.employee_group IN ({0})".format(employee_list)
	else:
		eg = ""
	
	if filters.get("project"):
		pmj = "and p.project = '{0}'".format(filters.get("project"))
		pj = "and t.project = '{0}'".format(filters.get("project"))
	else:
		pmj = ""
		pj = ""



	
	list_eps = []
	active_emp = []
	if filters.get("include_issues") == None:
		if filters.get("based_on") == "Team Lead" and filters.get("group_by") == "Project":
			tlc = frappe.db.sql("""
								select distinct
								p.project_lead,
								p.project_lead_name,
								(select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead and tk.status not in ("Template","Cancelled")) as assigned,
								(select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Completed") as completed,
								(select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue") as overdue,
								(select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status in ("Working","Pending Review","Open")) as working,
								(((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Completed")
								/(select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead and tk.status not in ("Template","Cancelled")))*100) as completion,


								(((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue")
								/(select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead and tk.status not in ("Template","Cancelled")))*100) as overdue_p,

								

								((((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue")
								+(select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status in ("Working","Pending Review","Open")))
								/((select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead)))*100) as pending

								FROM
									`tabTask` p
								JOIN `tabEmployee` e ON p.project_lead_name = e.employee_name
								WHERE
									e.status = 'Active'
					   			{0}
								""".format(tl,pmj),as_dict=1)

			for i in tlc:
				list_eps.append(i)
				team_lead = """
					t.project as project,
					p.project_name,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status not in ("Template","Cancelled"))) as assigned,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status = "Completed")) as completed,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status = "Overdue")) as overdue,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status in ("Working","Pending Review","Open"))) as working

					"""
			
				gpby = """group by t.project"""

				d_query = frappe.db.sql("""Select distinct {0} from `tabTask` t
											join `tabProject` p on p.name = t.project
											where 
											p.is_active = 'Yes' AND
											t.project_lead = '{2}'
											{3}
											{1}
										
				""".format(team_lead,gpby,i.get("project_lead"),pj),as_dict = 1)
			

				for items in d_query:

					if items.get("assigned") and items.get("completed"):
						tcp = (items.get("completed")/items.get("assigned"))*100
					else:
						tcp = 0

					if items.get("assigned") > 0:
						op = (items.get("overdue")/items.get("assigned"))*100
					else:
						op = 0


					if items.get("overdue") or items.get("working") and  items.get("assigned"):
						ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
						print("****************************9242",ptp)
					else:
						ptp = 0


					dynamic = frappe._dict({
						'project_lead': items.get("project_lead"),
						'project_lead_name': items.get("project_lead_name"),
						'project': items.get("project"),
						'project_name':items.get("project_name"),
						'assigned': items.get("assigned"),
						'completed':items.get("completed"),
						'overdue':items.get("overdue"),
						'working':items.get("working"),
						'completion':tcp,
						'overdue_p':op,
						'pending':ptp
						})

					list_eps.append(dynamic)


		if filters.get("based_on") == "Primary Consultant" and filters.get("group_by") == "Project":
			
			tlc = frappe.db.sql("""
								select distinct
								p.primary_consultant,
								p.primary_consultant_name,
								(select count(tk.name) from `tabTask` tk where tk.primary_consultant = p.primary_consultant and tk.status not in ("Template","Cancelled")) as assigned,
								(select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Completed") as completed,
								(select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Overdue") as overdue,
								(select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status in ("Working","Pending Review","Open")) as working,
								(((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Completed")
								/(select count(tk.name) from `tabTask` tk where tk.primary_consultant = p.primary_consultant and tk.status not in ("Template","Cancelled")))*100) as completion,

								(((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Overdue")
								/(select count(tk.name) from `tabTask` tk where tk.primary_consultant = p.primary_consultant and tk.status not in ("Template","Cancelled")))*100) as overdue_p,

								((((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Overdue")
								+(select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status in ("Working","Pending Review","Open")))
								/((select count(tk.name) from `tabTask` tk where tk.primary_consultant = p.primary_consultant)))*100) as pending

								from `tabTask` p
					   			JOIN
									`tabEmployee` e ON p.primary_consultant_name = e.employee_name
								
								WHERE
									e.status = 'Active' 
								{0}
								""".format(pc),as_dict = 1)
			print("**********************1234567******************9090",tlc)
			for i in tlc:
				list_eps.append(i)
				team_lead = """
					t.project as project,
					p.project_name,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status not in ("Template","Cancelled"))) as assigned,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status = "Completed")) as completed,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status = "Overdue")) as overdue,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status in ("Working","Pending Review","Open"))) as working

					"""
			
				gpby = """group by t.project"""

				d_query = frappe.db.sql("""Select distinct {0} from `tabTask` t
											join `tabProject` p on p.name = t.project
											
											where
											p.is_active = 'Yes' AND
											t.primary_consultant = '{2}'
											{3}
											{1}
											
				""".format(team_lead,gpby,i.get("primary_consultant"),pj),as_dict = 1)
	
				for items in d_query:
					
					if items.get("assigned") and items.get("completed"):
						tcp = (items.get("completed")/items.get("assigned"))*100
					else:
						tcp = 0

					
					if items.get("assigned") > 0:
						op = (items.get("overdue")/items.get("assigned"))*100
					else:
						op = 0


					if items.get("overdue") or items.get("working") and  items.get("assigned"):
						ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
						print("****************************9242",ptp)
					else:
						ptp = 0


					dynamic = frappe._dict({
						'primary_consultant': items.get("primary_consultant"),
						'primary_consultant_name': items.get("primary_consultant_name"),
						'project': items.get("project"),
						'project_name':items.get("project_name"),
						'assigned': items.get("assigned"),
						'completed':items.get("completed"),
						'overdue':items.get("overdue"),
						'working':items.get("working"),
						'completion':tcp,
						'overdue_p':op,
						'pending':ptp
						})
					
					list_eps.append(dynamic)
		
		if filters.get("based_on") == "Department" and filters.get("group_by") == "Project":
			
			tlc = frappe.db.sql("""
								select distinct
								p.department,
								(select count(tk.name) from `tabTask` tk where tk.department = p.department and tk.status not in ("Template","Cancelled")) as assigned,
								(select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Completed") as completed,
								(select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Overdue") as overdue,
								(select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status in ("Working","Pending Review","Open")) as working,
								(((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Completed")
								/(select count(tk.name) from `tabTask` tk where tk.department = p.department and tk.status not in ("Template","Cancelled")))*100) as completion,

								(((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Overdue")
								/(select count(tk.name) from `tabTask` tk where tk.department = p.department and tk.status not in ("Template","Cancelled")))*100) as overdue_p,

								((((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Overdue")
								+(select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status in ("Working","Pending Review","Open")))
								/((select count(tk.name) from `tabTask` tk where tk.department = p.department)))*100) as pending

								from `tabTask` p
								where 1=1
								{0}""".format(dp),as_dict = 1)
			
			for i in tlc:
				list_eps.append(i)
				team_lead = """
					distinct t.project as project,
					p.project_name,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.department = t.department and tk.status not in ("Template","Cancelled"))) as assigned,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.department = t.department and tk.status = "Completed")) as completed,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.department = t.department and tk.status = "Overdue")) as overdue,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.department = t.department and tk.status in ("Working","Pending Review","Open"))) as working

					"""
			
				gpby = """group by t.project"""

				d_query = frappe.db.sql("""Select distinct {0} from `tabTask` t
											join `tabProject` p on p.name = t.project
											where p.is_active = 'Yes' 
											AND t.department = '{2}'
											{3}
											{1}
				""".format(team_lead,gpby,i.get("department"),pj),as_dict = 1)
			

				for items in d_query:
					
					if items.get("assigned") and items.get("completed"):
						tcp = (items.get("completed")/items.get("assigned"))*100
					else:
						tcp = 0

					if items.get("assigned") > 0:
						op = (items.get("overdue")/items.get("assigned"))*100
					else:
						op = 0


					if items.get("overdue") or items.get("working") and  items.get("assigned"):
						ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
						print("****************************9242",ptp)
					else:
						ptp = 0


					dynamic = frappe._dict({
						'department': items.get("department"),
						'project': items.get("project"),
						'project_name':items.get("project_name"),
						'assigned': items.get("assigned"),
						'completed':items.get("completed"),
						'overdue':items.get("overdue"),
						'working':items.get("working"),
						'completion':tcp,
						'overdue_p':op,
						'pending':ptp
						})
					
					list_eps.append(dynamic)

		if filters.get("based_on") == "Employee Group" and filters.get("group_by") == "Project":
			
			if filters.get("employee_group"):
				employee_list = ", ".join(["'{}'".format(p.replace("'", "\\'")) for p in filters.get("employee_group")])
				egwp = "AND t.employee_group IN ({0})".format(employee_list)
			else:
				egwp = ""

			tlc = frappe.db.sql(f"""
				SELECT DISTINCT
					t.employee_group,
					(SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status NOT IN ('Template', 'Cancelled')) AS assigned,
					(SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status = 'Completed') AS completed,
					(SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status = 'Overdue') AS overdue,
					(SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status IN ('Working', 'Pending Review', 'Open')) AS working,
					((SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status = 'Overdue')
					/ (SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status NOT IN ('Template', 'Cancelled'))) * 100 AS overdue_p,
					((SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status = 'Completed')
					/ (SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status NOT IN ('Template', 'Cancelled'))) * 100 AS completion,
					(((SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status = 'Overdue')
					+ (SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group AND tk.status IN ('Working', 'Pending Review', 'Open')))
					/ (SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.employee_group = t.employee_group)) * 100 AS pending
				FROM `tabTask` t
				JOIN `tabEmployee` e
				JOIN `tabEmployee Group` eg
    			ON eg.group_lead_name = e.employee_name and t.employee_group = eg.name
				WHERE
					e.status = 'Active'
				{egwp}
			""", as_dict=True)

			print("*********************kkkk*******************9090", tlc)

			list_eps = []

			for i in tlc:
				list_eps.append(i)
				team_lead = f"""
					t.project AS project,
					p.project_name,
					(SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.project = t.project AND tk.employee_group = t.employee_group AND tk.status NOT IN ('Template', 'Cancelled')) AS assigned,
					(SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.project = t.project AND tk.employee_group = t.employee_group AND tk.status = 'Completed') AS completed,
					(SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.project = t.project AND tk.employee_group = t.employee_group AND tk.status = 'Overdue') AS overdue,
					(SELECT COUNT(tk.name) FROM `tabTask` tk WHERE tk.project = t.project AND tk.employee_group = t.employee_group AND tk.status IN ('Working', 'Pending Review', 'Open')) AS working
				"""

				gpby = "GROUP BY t.project"

				d_query = frappe.db.sql(f"""
					SELECT distinct {team_lead}
					FROM `tabTask` t
					JOIN `tabProject` p ON p.name = t.project
					WHERE p.is_active = 'Yes' 
					AND t.employee_group = '{i.get("employee_group")}'
					{gpby}
				""", as_dict=True)
	
# -------------------------------------------------------------------------------------------------
				for items in d_query:
					
					if items.get("assigned") and items.get("completed"):
						tcp = (items.get("completed")/items.get("assigned"))*100
					else:
						tcp = 0

					if items.get("assigned") > 0:
						op = (items.get("overdue")/items.get("assigned"))*100
					else:
						op = 0


					if items.get("overdue") or items.get("working") and  items.get("assigned"):
						ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
						print("****************************9242",ptp)
					else:
						ptp = 0


					dynamic = frappe._dict({
						'employee_group': items.get("employee_group"),
						'project': items.get("project"),
						'project_name':items.get("project_name"),
						'assigned': items.get("assigned"),
						'completed':items.get("completed"),
						'overdue':items.get("overdue"),
						'working':items.get("working"),
						'completion':tcp,
						'overdue_p':op,
						'pending':ptp
						})
					
					list_eps.append(dynamic)



		
# --------------------------------------------------------------------------------------------------
		

		elif filters.get("based_on") == "Team Lead" and not filters.get("group_by"):
			
			if filters.get("team_lead"):
				team_list = ", ".join(["'{}'".format(p.replace("'", "\\'")) for p in filters.get("team_lead")])
				egwp = "AND t.project_lead IN ({0})".format(team_list)
			else:
				egwp = ""

			tlc = """
				p.name as project_lead,
				p.employee_name as project_lead_name,
				(select count(tk.name) from `tabTask` tk where tk.project_lead = p.name and tk.status not in ('Template', 'Cancelled')) as assigned,
				(select count(tk.name) from `tabTask` tk where tk.project_lead = p.name and tk.status = 'Completed') as completed,
				(select count(tk.name) from `tabTask` tk where tk.project_lead = p.name and tk.status = 'Overdue') as overdue,
				(select count(tk.name) from `tabTask` tk where tk.project_lead = p.name and tk.status in ('Working', 'Pending Review', 'Open')) as working
			"""

			d_query = frappe.db.sql(f"""
				SELECT DISTINCT {tlc} 
				FROM `tabEmployee` p
				JOIN `tabTask` t ON t.project_lead_name = p.employee_name
				WHERE
					p.status = 'Active'
				{egwp}
				GROUP BY p.name
			""", as_dict=True)
					
# ----------------------------------------------------------------------------------------------------------------------
			for items in d_query:
				
				if items.get("assigned") and items.get("completed"):
					tcp = (items.get("completed")/items.get("assigned"))*100
				else:
					tcp = 0

				if items.get("assigned")>0:
					op = (items.get("overdue")/items.get("assigned"))*100
				else:
					op = 0


				if items.get("overdue") or items.get("working") and  items.get("assigned"):
					ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
					print("****************************9242",ptp)
				else:
					ptp = 0


				dynamic = frappe._dict({
					'project_lead': items.get("project_lead"),
					'project_lead_name': items.get("project_lead_name"),
					'assigned': items.get("assigned"),
					'completed':items.get("completed"),
					'overdue':items.get("overdue"),
					'working':items.get("working"),
					'completion':tcp,
					'overdue_p':op,
					'pending':ptp
					})
				

				
				list_eps.append(dynamic)

		
		

		elif filters.get("based_on") == "Department" and  not filters.get("group_by"):
			if filters.get("department"):
				dpwp = "where p.name = '{0}'".format(filters.get("department"))
			else:
				dpwp = ""
			

			# based_on_details["based_on_cols"] = ["Project Lead:Link/Employee:120", "Group Lead Name:Data:120"]
			tlc  = """p.name as department,
						((select count(tk.name) from `tabTask` tk where  tk.department = p.name and tk.status not in ("Template","Cancelled")) ) as assigned,
						((select count(tk.name) from `tabTask` tk where  tk.department = p.name and tk.status = "Completed") ) as completed,
						((select count(tk.name) from `tabTask` tk where  tk.department = p.name and tk.status = "Overdue") ) as overdue,
						((select count(tk.name) from `tabTask` tk where  tk.department = p.name and tk.status in ("Working","Pending Review","Open"))) as working

													"""
			d_query = frappe.db.sql("""Select distinct  {0} from `tabDepartment` p
											join `tabTask` t
											{1}
											group by p.name
				""".format(tlc,dpwp),as_dict = 1)
			

			for items in d_query:
				
				if items.get("assigned") and items.get("completed"):
					tcp = (items.get("completed")/items.get("assigned"))*100
				else:
					tcp = 0

				if items.get("assigned") > 0:
					op = (items.get("overdue")/items.get("assigned"))*100
				else:
					op = 0


				if items.get("overdue") or items.get("working") and  items.get("assigned"):
					ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
					print("****************************9242",ptp)
				else:
					ptp = 0


				dynamic = frappe._dict({
					'department': items.get("department"),
					'assigned': items.get("assigned"),
					'completed':items.get("completed"),
					'overdue':items.get("overdue"),
					'working':items.get("working"),
					'completion':tcp,
					'overdue_p':op,
					'pending':ptp
					})
				

				
				list_eps.append(dynamic)

# -------------------------------------------------------------------------------------
		
		elif filters.get("based_on") == "Primary Consultant" and  not filters.get("group_by"):
			primary_cond=[]
			if filters.get("primary_consultant"):
				# pcwp = "where p.name = '{0}'".format(filters.get("primary_consultant"))
				primary_consultant_list = ", ".join([f"'{p.strip()}'" for p in filters.get("primary_consultant")])
				# primary_cond.append(f"p.name IN ({primary_consultant_list})")
				pcwp = "AND p.name IN ({0})".format(primary_consultant_list)

			else:
				pcwp = ""
			print("tl,"",ii9242")

			# based_on_details["based_on_cols"] = ["Project Lead:Link/Employee:120", "Group Lead Name:Data:120"]
			tlc  = """p.name as primary_consultant,
						p.employee_name as primary_consultant_name,
						((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status not in ("Template","Cancelled")) ) as assigned,
						((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status = "Completed") ) as completed,
						((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status = "Overdue") ) as overdue,
						((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status in ("Working","Pending Review","Open"))) as working

													"""
			d_query = frappe.db.sql("""Select distinct  {0} from `tabEmployee` p
											JOIN `tabTask` t ON t.project_lead_name = p.employee_name
											WHERE
												p.status = 'Active'
											{1}
											group by p.name
				""".format(tlc,pcwp),as_dict = 1)
			

# -----------------------------------------------------------------------------------------------------
			for items in d_query:
				
				if items.get("assigned") and items.get("completed"):
					tcp = (items.get("completed")/items.get("assigned"))*100
				else:
					tcp = 0

				if items.get("assigned")>0:
					op = (items.get("overdue")/items.get("assigned"))*100
				else:
					op = 0


				if items.get("overdue") or items.get("working") and  items.get("assigned"):
					ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
					print("****************************9242",ptp)
				else:
					ptp = 0


				dynamic = frappe._dict({
					'primary_consultant': items.get("primary_consultant"),
					'primary_consultant_name': items.get("primary_consultant_name"),
					'assigned': items.get("assigned"),
					'completed':items.get("completed"),
					'overdue':items.get("overdue"),
					'working':items.get("working"),
					'completion':tcp,
					'overdue_p':op,
					'pending':ptp
					})
			
				list_eps.append(dynamic)
# ------------------------------------------------------------------------------------------------

		if filters.get("based_on") == "Employee Group" and not filters.get("group_by"):
			emp_cond = []
			if filters.get("employee_group"):
				employee_list = ", ".join(["'{}'".format(p.replace("'", "\\'")) for p in filters.get("employee_group")])
				egwp = "AND t.employee_group IN ({0})".format(employee_list)
			else:
				egwp = ""

			print("&&&&&&&&&&&&&&&&&&&&&&&&&&  tl, '', ii &&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

			tlc = """
				p.name as employee_group,
				(select count(tk.name) from `tabTask` tk where tk.employee_group = p.name and tk.status not in ('Template', 'Cancelled')) as assigned,
				(select count(tk.name) from `tabTask` tk where tk.employee_group = p.name and tk.status = 'Completed') as completed,
				(select count(tk.name) from `tabTask` tk where tk.employee_group = p.name and tk.status = 'Overdue') as overdue,
				(select count(tk.name) from `tabTask` tk where tk.employee_group = p.name and tk.status in ('Working', 'Pending Review', 'Open')) as working
			"""

			d_query = frappe.db.sql(f"""
				SELECT DISTINCT {tlc} 
				FROM `tabEmployee Group` p
				JOIN `tabTask` t ON t.employee_group = p.name
    			JOIN `tabEmployee` e ON p.group_lead_name = e.employee_name and t.employee_group = p.name
				WHERE
					e.status = 'Active'
				{egwp}
				GROUP BY p.name
			""", as_dict=True)
			
# ------------------------------------------------------------------------------------------------------
			for items in d_query:
				
				if items.get("assigned") and items.get("completed"):
					tcp = (items.get("completed")/items.get("assigned"))*100
				else:
					tcp = 0

				if items.get("assigned") > 0:
					op = (items.get("overdue")/items.get("assigned"))*100
				else:
					op = 0


				if items.get("overdue") or items.get("working") and  items.get("assigned"):
					ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
					print("****************************9242",ptp)
				else:
					ptp = 0


				dynamic = frappe._dict({
					'employee_group': items.get("employee_group"),
					'assigned': items.get("assigned"),
					'completed':items.get("completed"),
					'overdue':items.get("overdue"),
					'working':items.get("working"),
					'completion':tcp,
					'overdue_p':op,
					'pending':ptp
					})
				
				list_eps.append(dynamic)


	if filters.get("include_issues") == 1:
		print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
		# overdue = """select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue" """
		# working = """select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status in ("Working","Pending Review","Open") """
		# assigned = """select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead"""
		# pending = ((overdue) + (working)/(assigned))

		# tl_list= []
		if filters.get("based_on") == "Team Lead" and filters.get("group_by") == "Project":
			if filters.get("employee_group"):
				teaml_list = ", ".join([f"'{p.strip()}'" for p in filters.get("team_lead")])
				tl = "AND p.project_lead IN ({0})".format(teaml_list)
			else:
				tl = ""
			tlc = frappe.db.sql("""
								select distinct
								p.project_lead,
								p.project_lead_name,
								((select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.project_lead = p.project_lead and tk.status = "Open")) as assigned,
								((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Completed") + (select count(tk.name) from `tabIssue` tk where tk.project_lead = p.project_lead and tk.status = "Closed" or tk.status = "Resolved")) as completed,
								((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue")) as overdue,
								((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status in ("Working","Pending Review","Open"))) as working,

								((((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Completed") + (select count(tk.name) from `tabIssue` tk where tk.project_lead = p.project_lead and tk.status = "Closed" or tk.status = "Resolved"))
								/((select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.project_lead = p.project_lead and tk.status = "Open")))*100) as completion,

								(((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue")/
								(select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead and tk.status not in ("Template","Cancelled")))*100) as overdue_p,

								(((((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status = "Overdue"))
								+((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.project_lead and tk.status in ("Working","Pending Review","Open"))))
								/((select count(tk.name) from `tabTask` tk where tk.project_lead = p.project_lead and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.project_lead = p.project_lead and tk.status = "Open")))*100) as pending

								from `tabTask` p
								WHERE 1=1
								{0}
								
								""".format(tl),as_dict = 1)
			print("****************************************9090",tlc)
			for i in tlc:
				list_eps.append(i)
				team_lead = """
					t.project as project,
					p.project_name,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status not in ("Template","Cancelled"))+ (select count(i.name) from `tabIssue` i where i.project = t.project and i.project_lead = t.project_lead and i.status = "Open")) as assigned,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status = "Completed")  + (select count(tk.name) from `tabIssue` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status = "Closed" or tk.status = "Resolved")) as completed,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status = "Overdue")) as overdue,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.project_lead = t.project_lead and tk.status in ("Working","Pending Review","Open"))) as working

					"""
			


			
				
				gpby = """group by t.project"""

				print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",gpby)

				d_query = frappe.db.sql("""Select distinct {0} from `tabTask` t
											join `tabProject` p on p.name= t.project
											join `tabIssue` i
											where 
											p.is_active = 'Yes' AND
											t.project_lead = '{2}'
											{3}
											{1}
				""".format(team_lead,gpby,i.get("project_lead"),pj),as_dict = 1)
			

				for items in d_query:
					
					if items.get("assigned") and items.get("completed"):
						tcp = (items.get("completed")/items.get("assigned"))*100
					else:
						tcp = 0

					if items.get("assigned") > 0:
						op = (items.get("overdue")/items.get("assigned"))*100
					else:
						op = 0


					if items.get("overdue") or items.get("working") and  items.get("assigned"):
						ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
						print("****************************9242",ptp)
					else:
						ptp = 0


					dynamic = frappe._dict({
						'project_lead': items.get("project_lead"),
						'project_lead_name': items.get("project_lead_name"),
						'project': items.get("project"),
						'project_name':items.get("project_name"),
						'assigned': items.get("assigned"),
						'completed':items.get("completed"),
						'overdue':items.get("overdue"),
						'working':items.get("working"),
						'completion':tcp,
						'overdue_p':op,
						'pending':ptp
						})
					

					
					list_eps.append(dynamic)


		if filters.get("based_on") == "Primary Consultant" and filters.get("group_by") == "Project":
			print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
			tlc = frappe.db.sql("""
								select distinct
								p.primary_consultant,
								p.primary_consultant_name,
								((select count(tk.name) from `tabTask` tk where tk.primary_consultant = p.primary_consultant and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.primary_consultant = p.primary_consultant and tk.status = "Open")) as assigned,
								((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Completed") + (select count(tk.name) from `tabIssue` tk where tk.primary_consultant = p.primary_consultant and tk.status = "Closed" or tk.status = "Resolved")) as completed,
								((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Overdue")) as overdue,
								((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status in ("Working","Pending Review","Open"))) as working,

								((((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Completed") + (select count(tk.name) from `tabIssue` tk where tk.primary_consultant = p.primary_consultant and tk.status = "Closed" or tk.status = "Resolved"))
								/((select count(tk.name) from `tabTask` tk where tk.primary_consultant = p.primary_consultant and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.primary_consultant = p.primary_consultant and tk.status = "Open")))*100) as completion,

								((((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Overdue"))
								/((select count(tk.name) from `tabTask` tk where tk.primary_consultant = p.primary_consultant and tk.status not in ("Template","Cancelled"))))*100) as overdue_p,

								(((((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status = "Overdue"))
								+((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.primary_consultant and tk.status in ("Working","Pending Review","Open"))))
								/((select count(tk.name) from `tabTask` tk where tk.primary_consultant = p.primary_consultant and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.primary_consultant = p.primary_consultant and tk.status = "Open")))*100) as pending

								from `tabTask` p
					   			WHERE 1=1
								{0}
								""".format(pc),as_dict = 1)
			print("*********************kkkkkkkkkkk*******************9090",tlc)
			for i in tlc:
				list_eps.append(i)
				team_lead = """
					t.project as project,
					p.project_name,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status not in ("Template","Cancelled"))+ (select count(i.name) from `tabIssue` i where i.project = t.project and i.primary_consultant = t.primary_consultant and i.status = "Open")) as assigned,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status = "Completed")  + (select count(tk.name) from `tabIssue` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status = "Closed" or tk.status = "Resolved")) as completed,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status = "Overdue")) as overdue,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.primary_consultant = t.primary_consultant and tk.status in ("Working","Pending Review","Open"))) as working

					"""
			


			
				
				gpby = """group by t.project"""

				

				d_query = frappe.db.sql("""Select distinct {0} from `tabTask` t
											join `tabProject` p on p.name = t.project
											
											where 
											p.is_active = 'Yes' AND
											t.primary_consultant = '{2}'
											{3}
											{1}
				""".format(team_lead,gpby,i.get("primary_consultant"),pj),as_dict = 1)
			

				for items in d_query:
					
					if items.get("assigned") and items.get("completed"):
						tcp = (items.get("completed")/items.get("assigned"))*100
					else:
						tcp = 0

					if items.get("assigned") > 0:
						op = (items.get("overdue")/items.get("assigned"))*100
					else:
						op = 0


					if items.get("overdue") or items.get("working") and  items.get("assigned"):
						ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
						print("****************************9242",ptp)
					else:
						ptp = 0


					dynamic = frappe._dict({
						'primary_consultant': items.get("primary_consultant"),
						'primary_consultant_name': items.get("primary_consultant_name"),
						'project': items.get("project"),
						'project_name':items.get("project_name"),
						'assigned': items.get("assigned"),
						'completed':items.get("completed"),
						'overdue':items.get("overdue"),
						'working':items.get("working"),
						'completion':tcp,
						'overdue_p':op,
						'pending':ptp
						})
					

					
					list_eps.append(dynamic)
		
		if filters.get("based_on") == "Department" and filters.get("group_by") == "Project":
			tlc = frappe.db.sql("""
								select distinct
								p.department,
								((select count(tk.name) from `tabTask` tk where tk.department = p.department and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.department_ = p.department and tk.status = "Open")) as assigned,
								((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Completed")+(select count(tk.name) from `tabIssue` tk where tk.department_ = p.department and tk.status = "Closed" or tk.status = "Resolved")) as completed,
								(select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Overdue") as overdue,
								(select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status in ("Working","Pending Review","Open")) as working,

								((((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Completed")+(select count(tk.name) from `tabIssue` tk where tk.department_ = p.department and tk.status = "Closed" or tk.status = "Resolved"))
								/((select count(tk.name) from `tabTask` tk where tk.department = p.department and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.department_ = p.department and tk.status = "Open")))*100) as completion,

								((((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Overdue")/
								(select count(tk.name) from `tabTask` tk where tk.department = p.department and tk.status not in ("Template","Cancelled"))))*100) as overdue_p,

								((((select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status = "Overdue")
								+(select count(tk.name) from `tabTask` tk where  tk.department = p.department and tk.status in ("Working","Pending Review","Open")))
								/(((select count(tk.name) from `tabTask` tk where tk.department = p.department and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.department_ = p.department and tk.status = "Open"))))*100) as pending

								from `tabTask` p
					   			WHERE 1=1
								{0}
								""".format(dp),as_dict = 1)
			print("****************************************9090",tlc)
			for i in tlc:
				list_eps.append(i)
				team_lead = """
					t.project as project,
					p.project_name,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.department = t.department and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.project = t.project and tk.department_ = t.department and tk.status = "Open")) as assigned,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.department = t.department and tk.status = "Completed")+(select count(tk.name) from `tabIssue` tk where tk.project = t.project and tk.department_ = t.department and tk.status = "Closed" or tk.status = "Resolved")) as completed,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.department = t.department and tk.status = "Overdue")) as overdue,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.department = t.department and tk.status in ("Working","Pending Review","Open"))) as working

					"""
			
				gpby = """group by t.project"""

				# d_query = frappe.db.sql("""Select distinct {0} from `tabTask` t
				# 							join `tabProject` p on p.name = t.project
											
				# 							where 
				# 							p.is_active = 'Yes' AND
				# 							t.department = '{2}'
				# 							{3}
				# 							{1}
				# """.format(team_lead,gpby,i.get("department"),pj),as_dict = 1)

				d_query = frappe.db.sql("""
					SELECT DISTINCT {0} 
					FROM `tabTask` t
					JOIN `tabProject` p ON p.name = t.project
					WHERE 
						p.is_active = 'Yes' 
						AND t.department = '{2}'
						{3}
						{1}
        		""".format(team_lead, gpby, i.get("department"), pj), as_dict=1)
			

				for items in d_query:
					
					if items.get("assigned") and items.get("completed"):
						tcp = (items.get("completed")/items.get("assigned"))*100
					else:
						tcp = 0

					if items.get("assigned")>0:
						op = (items.get("overdue")/items.get("assigned"))*100
					else:
						op = 0


					if items.get("overdue") or items.get("working") and  items.get("assigned"):
						ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
						print("****************************9242",ptp)
					else:
						ptp = 0


					dynamic = frappe._dict({
						'department': items.get("department"),
						'project': items.get("project"),
						'project_name':items.get("project_name"),
						'assigned': items.get("assigned"),
						'completed':items.get("completed"),
						'overdue':items.get("overdue"),
						'working':items.get("working"),
						'completion':tcp,
						'overdue_p':op,
						'pending':ptp
						})
					

					
					list_eps.append(dynamic)
		
		if filters.get("based_on") == "Employee Group" and filters.get("group_by") == "Project":
			tlc = frappe.db.sql("""
								select distinct
								p.employee_group,
								((select count(tk.name) from `tabTask` tk where tk.employee_group = p.employee_group and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.employee_group = p.employee_group and tk.status = "Open")) as assigned,
								((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status = "Completed")+(select count(tk.name) from `tabIssue` tk where tk.employee_group = p.employee_group and tk.status = "Closed" or tk.status = "Resolved")) as completed,
								(select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status = "Overdue") as overdue,
								(select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status in ("Working","Pending Review","Open")) as working,

								((((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status = "Completed")+(select count(tk.name) from `tabIssue` tk where tk.employee_group = p.employee_group and tk.status = "Closed" or tk.status = "Resolved"))
								/((select count(tk.name) from `tabTask` tk where tk.employee_group = p.employee_group and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.employee_group = p.employee_group and tk.status = "Open")))*100) as completion,

								((((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status = "Overdue")/
								(select count(tk.name) from `tabTask` tk where tk.employee_group = p.employee_group and tk.status not in ("Template","Cancelled"))))*100) as overdue_p,

								((((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status = "Overdue")
								+(select count(tk.name) from `tabTask` tk where  tk.employee_group = p.employee_group and tk.status in ("Working","Pending Review","Open")))
								/(((select count(tk.name) from `tabTask` tk where tk.employee_group = p.employee_group and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.employee_group = p.employee_group and tk.status = "Open"))))*100) as pending

								from `tabTask` p
					   			WHERE 1=1
								{0}
								""".format(eg),as_dict = 1)
			print("****************************************9090",tlc)
			for i in tlc:
				list_eps.append(i)
				team_lead = """
					t.project as project,
					p.project_name,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.employee_group = t.employee_group and tk.status not in ("Template","Cancelled"))+(select count(tk.name) from `tabIssue` tk where tk.project = t.project and tk.employee_group = t.employee_group and tk.status = "Open")) as assigned,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.employee_group = t.employee_group and tk.status = "Completed")+(select count(tk.name) from `tabIssue` tk where tk.project = t.project and tk.employee_group = t.employee_group and tk.status = "Closed" or tk.status = "Resolved")) as completed,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.employee_group = t.employee_group and tk.status = "Overdue")) as overdue,
					((select count(tk.name) from `tabTask` tk where tk.project = t.project and tk.employee_group = t.employee_group and tk.status in ("Working","Pending Review","Open"))) as working

					"""
			


			
				
				gpby = """group by t.project"""

				

				d_query = frappe.db.sql("""Select distinct {0} from `tabTask` t
											join `tabProject` p on p.name = t.project
											join `tabIssue` i
											where 
											p.is_active = 'Yes' AND
											p.employee_group = '{2}'
											{3}
											{1}
				""".format(team_lead,gpby,i.get("employee_group"),pj),as_dict = 1)
			

				for items in d_query:
					
					if items.get("assigned") and items.get("completed"):
						tcp = (items.get("completed")/items.get("assigned"))*100
					else:
						tcp = 0

					if items.get("assigned") >0:
						op = (items.get("overdue")/items.get("assigned"))*100
					else:
						op = 0


					if items.get("overdue") or items.get("working") and  items.get("assigned"):
						ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
						print("****************************9242",ptp)
					else:
						ptp = 0


					dynamic = frappe._dict({
						'employee_group': items.get("employee_group"),
						'project': items.get("project"),
						'project_name':items.get("project_name"),
						'assigned': items.get("assigned"),
						'completed':items.get("completed"),
						'overdue':items.get("overdue"),
						'working':items.get("working"),
						'completion':tcp,
						'overdue_p':op,
						'pending':ptp
						})
					
					list_eps.append(dynamic)



		

		

		elif filters.get("based_on") == "Team Lead" and  not filters.get("group_by"):
			if filters.get("team_lead"):
				team_list = ", ".join(["'{}'".format(p.replace("'", "\\'")) for p in filters.get("team_lead")])
				tlwpi = "AND t.project_lead IN ({0})".format(team_list)
			else:
				tlwpi = ""

			print("tl,"",ii","abc")

			# based_on_details["based_on_cols"] = ["Project Lead:Link/Employee:120", "Group Lead Name:Data:120"]
			tlc  = """p.name as project_lead,
						p.employee_name as project_lead_name,
						((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.name and tk.status not in ("Template","Cancelled"))+ (select count(tk.name) from `tabIssue` tk where  tk.project_lead = p.name and tk.status = "Open")) as assigned,
						(select count(tk.name) from `tabTask` tk where  tk.project_lead = p.name and tk.status not in ("Template","Cancelled")) as atk,
						((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.name and tk.status = "Completed") + (select count(tk.name) from `tabIssue` tk where  tk.project_lead = p.name and tk.status = "Closed" or tk.status = "Resolved")) as completed,
						((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.name and tk.status = "Overdue") ) as overdue,
						((select count(tk.name) from `tabTask` tk where  tk.project_lead = p.name and tk.status in ("Working","Pending Review","Open"))) as working

													"""
			d_query = frappe.db.sql("""Select distinct  {0} from `tabEmployee` p
											JOIN tabTask t ON t.project_lead_name = p.employee_name
											WHERE p.status = 'Active' {1}
											GROUP BY p.name
				""".format(tlc,tlwpi),as_dict = 1)
			

			for items in d_query:
				
				if items.get("assigned") and items.get("completed"):
					tcp = (items.get("completed")/items.get("assigned"))*100
				else:
					tcp = 0

				if items.get("assigned") >0:
					op = (items.get("overdue")/items.get("atk"))*100
				else:
					op = 0


				if items.get("overdue") or items.get("working") and  items.get("assigned"):
					ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
					print("****************************9242",ptp)
				else:
					ptp = 0


				dynamic = frappe._dict({
					'project_lead': items.get("project_lead"),
					'project_lead_name': items.get("project_lead_name"),
					'assigned': items.get("assigned"),
					'completed':items.get("completed"),
					'overdue':items.get("overdue"),
					'working':items.get("working"),
					'overdue_p':op,
					'completion':tcp,
					'pending':ptp
					})
				
				list_eps.append(dynamic)

		
		elif filters.get("based_on") == "Primary Consultant" and  not filters.get("group_by"):
			if filters.get("primary_consultant"):
				primary_consultant_list = ", ".join([f"'{p.strip()}'" for p in filters.get("primary_consultant")])
				# primary_cond.append(f"p.name IN ({primary_consultant_list})")
				pcwpi = "AND p.name IN ({0})".format(primary_consultant_list)
			else:
				pcwpi = ""
			print("tl,"",ii")

			# based_on_details["based_on_cols"] = ["Project Lead:Link/Employee:120", "Group Lead Name:Data:120"]
			tlc  = """p.name as primary_consultant,
						p.employee_name as primary_consultant_name,
						((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status not in ("Template","Cancelled"))+ (select count(tk.name) from `tabIssue` tk where  tk.primary_consultant = p.name and tk.status = "Open")) as assigned,
						(select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status not in ("Template","Cancelled")) as atk,
						((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status = "Completed")+ (select count(tk.name) from `tabIssue` tk where  tk.primary_consultant = p.name and tk.status = "Open")) as completed,
						((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status = "Overdue") ) as overdue,
						((select count(tk.name) from `tabTask` tk where  tk.primary_consultant = p.name and tk.status in ("Working","Pending Review","Open"))) as working

													"""
			d_query = frappe.db.sql("""Select distinct {0} from `tabEmployee` p
											join `tabTask` t ON t.project_lead_name = p.employee_name
											WHERE
												p.status = 'Active'
											{1}
											group by p.name
				""".format(tlc,pcwpi),as_dict = 1)
			

			for items in d_query:
				
				if items.get("assigned") and items.get("completed"):
					tcp = (items.get("completed")/items.get("assigned"))*100
				else:
					tcp = 0

				if items.get("assigned")>0:
					op = (items.get("overdue")/items.get("atk"))*100
				else:
					op = 0


				if items.get("overdue") or items.get("working") and  items.get("assigned"):
					ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
					print("****************************9242",ptp)
				else:
					ptp = 0


				dynamic = frappe._dict({
					'primary_consultant': items.get("primary_consultant"),
					'primary_consultant_name': items.get("primary_consultant_name"),
					'assigned': items.get("assigned"),
					'completed':items.get("completed"),
					'overdue':items.get("overdue"),
					'working':items.get("working"),
					'completion':tcp,
					'overdue_p':op,
					'pending':ptp
					})
				
				list_eps.append(dynamic)

		elif filters.get("based_on") == "Department" and  not filters.get("group_by"):
			if filters.get("department"):
				dwpi = "where p.name = '{0}'".format(filters.get("department"))
			else:
				dwpi = ""
			print("tl,"",ii,abc")

			# based_on_details["based_on_cols"] = ["Project Lead:Link/Employee:120", "Group Lead Name:Data:120"]
			tlc  = """p.name as department,
						((select count(tk.name) from `tabTask` tk where  tk.department = p.name and tk.status not in ("Template","Cancelled")) + (select count(tk.name) from `tabIssue` tk  where  tk.department_ = p.name and tk.status = "Open")) as assigned,
						(select count(tk.name) from `tabTask` tk where  tk.department = p.name and tk.status not in ("Template","Cancelled")) as atk,
						((select count(tk.name) from `tabTask` tk where  tk.department = p.name and tk.status = "Completed")+ (select count(tk.name) from `tabIssue` tk where  tk.department_ = p.name and   tk.status = "Closed" or tk.status = "Resolved")) as completed,
						((select count(tk.name) from `tabTask` tk where  tk.department = p.name and   tk.status = "Overdue") ) as overdue,
						((select count(tk.name) from `tabTask` tk where  tk.department = p.name and   tk.status in ("Working","Pending Review","Open"))) as working

													"""
			d_query = frappe.db.sql("""Select distinct  {0} from `tabDepartment` p
											join `tabTask` t
											{1}
											group by p.name
				""".format(tlc,dwpi),as_dict = 1)
			

			for items in d_query:
				
				if items.get("assigned") and items.get("completed"):
					tcp = (items.get("completed")/items.get("assigned"))*100
				else:
					tcp = 0

				if items.get("atk")>0:
					op = (items.get("overdue")/items.get("atk"))*100
				else:
					op = 0


				if items.get("overdue") or items.get("working") and  items.get("assigned"):
					ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
					print("****************************9242",ptp)
				else:
					ptp = 0


				dynamic = frappe._dict({
					'department': items.get("department"),
					'assigned': items.get("assigned"),
					'completed':items.get("completed"),
					'overdue':items.get("overdue"),
					'working':items.get("working"),
					'completion':tcp,
					'overdue_p':op,
					'pending':ptp
					})
				
				list_eps.append(dynamic)

		
		

		elif filters.get("based_on") == "Employee Group" and  not filters.get("group_by"):
			if filters.get("employee_group"):
				employee_list = ", ".join(["'{}'".format(p.replace("'", "\\'")) for p in filters.get("employee_group")])
				egwpi = "AND p.name IN ({0})".format(employee_list)
			else:
				egwpi = ""
			print("tl,"",ii,abc")
			tlc  = """p.name as employee_group,
						((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.name and tk.status not in ("Template","Cancelled"))+ (select count(tk.name) from `tabIssue` tk where  tk.employee_group = p.name and tk.status = "Open")) as assigned,
						(select count(tk.name) from `tabTask` tk where  tk.employee_group = p.name and tk.status not in ("Template","Cancelled")) as atk,
						((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.name and tk.status = "Completed")+ (select count(tk.name) from `tabIssue` tk where  tk.employee_group = p.name and tk.status = "Closed" or tk.status = "Resolved")) as completed,
						((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.name and tk.status = "Overdue") ) as overdue,
						((select count(tk.name) from `tabTask` tk where  tk.employee_group = p.name and tk.status in ("Working","Pending Review","Open"))) as working

													"""
			d_query = frappe.db.sql("""Select distinct {0} from `tabEmployee Group` p
											join `tabTask` t ON t.employee_group = p.name
											JOIN `tabEmployee` e ON p.group_lead_name = e.employee_name and t.employee_group = p.name
											WHERE
												e.status = 'Active'
											{1}
											group by p.name
											
				""".format(tlc,egwpi),as_dict = 1)
			

			for items in d_query:
				
				if items.get("assigned") and items.get("completed"):
					tcp = (items.get("completed")/items.get("assigned"))*100
				else:
					tcp = 0

				if items.get("atk") >0:
					op = (items.get("overdue")/items.get("atk"))*100
				else:
					op = 0


				if items.get("overdue") or items.get("working") and  items.get("assigned"):
					ptp = ((items.get("overdue") + items.get("working"))/items.get("assigned"))*100
				else:
					ptp = 0


				dynamic = frappe._dict({
					'employee_group': items.get("employee_group"),
					'assigned': items.get("assigned"),
					'completed':items.get("completed"),
					'overdue':items.get("overdue"),
					'working':items.get("working"),
					'completion':tcp,
					'overdue_p':op,
					'pending':ptp
					})
				list_eps.append(dynamic)
	

	print("*****************list_eps****************",list_eps)
	
	return list_eps


def get_chart_data(data,filters):
	labels = []
	total = []
	completed = []
	overdue = []
	working = []

	# data = frappe.db.get_all('Task',{})
	if filters.get("group_by") == "Project":

		if filters.get("project"):
			proj = "and pj.name = '{0}' ".format(filters.get("project"))
		else:
			proj = ""

		if filters.get("include_issues") == None:
			pj = frappe.db.sql("""
									select pj.name from `tabProject` pj 
									where pj.is_active = "Yes"
									{0}

			""".format(proj),as_dict=True)
			if pj:
				for i in pj:
					labels.append(i.get("name"))
					tt = frappe.db.count('Task',{'project':i.get("name"),'status':["not in",["Cancelled,Template"]]})
					total.append(tt)
					cp = frappe.db.count('Task',{'project':i.get("name"),'status':"Completed"})
					completed.append(cp)
					od = frappe.db.count('Task',{'project':i.get("name"),'status':"Overdue"})
					overdue.append(od)
					wk = frappe.db.count('Task',{'project':i.get("name"),'status':["in",["Working","Pending Review","Open"]]})
					working.append(wk)
				
				return {
				"data": {
					'labels': labels[:30],
					'datasets': [
						{
							"name": "Overdue Tasks",
							"values": overdue[:30]
						},
						{
							"name": "Completed Tasks",
							"values": completed[:30]
						},
						{
							"name": "Working Tasks",
							"values":working[:30]
						}
						# {
						# 	"name": "Total Tasks",
						# 	"values": total[:30]
						# },
					]
				},
				"type": "bar",
				"colors": ["#fc4f51", "#228B22", "#FFA500"],
				"barOptions": {
					"stacked": False
				}
			}

		elif filters.get("include_issues") == 1:
			
			pj = frappe.db.sql("""
									select pj.name from `tabProject` pj 
									where pj.is_active = "Yes"
									{0}

			""".format(proj),as_dict=True)
			if pj:
				for i in pj:
					labels.append(i.get("name"))
					tt = frappe.db.count('Task',{'project':i.get("name"),'status':["not in",["Template","Cancelled"]]})
					ti = frappe.db.count('Issue',{'project':i.get("name"),'status':"Open"})
					total.append(tt+ti)
					cp = frappe.db.count('Task',{'project':i.get("name"),'status':"Completed"})
					ci = frappe.db.count('Issue',{'project':i.get("name"),'status':["in",["Resolved","Closed"]]})
					completed.append(cp+ci)
					od = frappe.db.count('Task',{'project':i.get("name"),'status':"Overdue"})
					
					overdue.append(od)
					wk = frappe.db.count('Task',{'project':i.get("name"),'status':["in",["Working","Pending Review","Open"]]})
					wi = frappe.db.count('Issue',{'project':i.get("name"),'status':"Open"})
					working.append(wk+wi)
					
				
				return {
				"data": {
					'labels': labels[:30],
					'datasets': [
						{
							"name": "Overdue(Tasks)",
							"values": overdue[:30]
						},
						{
							"name": "Completed(Tasks+Issues)",
							"values": completed[:30]
						},
						{
							"name": "Working(Tasks+Issues)",
							"values":working[:30]
						},
						# {
						# 	"name": "Total Tasks(Tasks+Issues)",
						# 	"values": total[:30]
						# },
					]
				},
				"type": "bar",
				"colors": ["#fc4f51", "#228B22", "#FFA500"],
				"barOptions": {
					"stacked": False
				}
			}

	else:
		if filters.get("based_on") == "Team Lead":
		
			for i in data:
					labels.append(i.get("project_lead"))
					
					total.append(i.get("assigned"))
					
					completed.append(i.get("completed"))
					
					overdue.append(i.get("overdue"))
					
					working.append(i.get("working"))
				
			return {
				"data": {
					'labels': labels[:30],
					'datasets': [
						{
							"name": "Overdue Tasks",
							"values": overdue[:30]
						},
						{
							"name": "Completed Tasks",
							"values": completed[:30]
						},
						{
							"name": "Working Tasks",
							"values":working[:30]
						},
						# {
						# 	"name": "Total Tasks",
						# 	"values": total[:30]
						# },
					]
				},
				"type": "bar",
				"colors": ["#fc4f51", "#228B22", "#FFA500","#89CFF0"],
				"barOptions": {
					"stacked": False
				}
			}

		if filters.get("based_on") == "Primary Consultant":
		
			for i in data:
					labels.append(i.get("primary_consultant"))
					
					total.append(i.get("assigned"))
					
					completed.append(i.get("completed"))
					
					overdue.append(i.get("overdue"))
					
					working.append(i.get("working"))
				
			return {
				"data": {
					'labels': labels[:30],
					'datasets': [
						{
							"name": "Overdue Tasks",
							"values": overdue[:30]
						},
						{
							"name": "Completed Tasks",
							"values": completed[:30]
						},
						{
							"name": "Working Tasks",
							"values":working[:30]
						},
						# {
						# 	"name": "Total Tasks",
						# 	"values": total[:30]
						# },
					]
				},
				"type": "bar",
				"colors": ["#fc4f51", "#228B22", "#FFA500","#89CFF0"],
				"barOptions": {
					"stacked": False
				}
			}
		if filters.get("based_on") == "Employee Group":
		
			for i in data:
					labels.append(i.get("employee_group"))
					
					total.append(i.get("assigned"))
					
					completed.append(i.get("completed"))
					
					overdue.append(i.get("overdue"))
					
					working.append(i.get("working"))
				
			return {
				"data": {
					'labels': labels[:30],
					'datasets': [
						{
							"name": "Overdue Tasks",
							"values": overdue[:30]
						},
						{
							"name": "Completed Tasks",
							"values": completed[:30]
						},
						{
							"name": "Working Tasks",
							"values":working[:30]
						},
						# {
						# 	"name": "Total Tasks",
						# 	"values": total[:30]
						# },
					]
				},
				"type": "bar",
				"colors": ["#fc4f51", "#228B22", "#FFA500","#89CFF0"],
				"barOptions": {
					"stacked": False
				}
			}

		if filters.get("based_on") == "Department":
		
			for i in data:
					labels.append(i.get("department"))
					
					total.append(i.get("assigned"))
					
					completed.append(i.get("completed"))
					
					overdue.append(i.get("overdue"))
					
					working.append(i.get("working"))
				
			return {
				"data": {
					'labels': labels[:30],
					'datasets': [
						{
							"name": "Overdue Tasks",
							"values": overdue[:30]
						},
						{
							"name": "Completed Tasks",
							"values": completed[:30]
						},
						{
							"name": "Working Tasks",
							"values":working[:30]
						},
						# {
						# 	"name": "Total Tasks",
						# 	"values": total[:30]
						# },
					]
				},
				"type": "bar",
				"colors": ["#fc4f51", "#228B22", "#FFA500","#89CFF0"],
				"barOptions": {
					"stacked": False
				}
			}

def get_report_summary(filters, data):
	filtered_data=[]
	employee_data={
		"overdue_task":0,
		"working_task":0,
		"completed_task":0,
		"total_task":0
	}
	for d in data:
		if d.get("primary_consultant"):
			employee_data["overdue_task"]+=d.get("overdue")
			employee_data["working_task"]+=d.get("working")
			employee_data["completed_task"]+=d.get("completed")
			if d.get("primary_consultant") is None:
				employee_data["overdue_task"]+=d.get("overdue")
				employee_data["working_task"]+=d.get("working")
				employee_data["completed_task"]+=d.get("completed")
				
			print("stasiiiiiiiiiiiiiiiiiiiiiiiiiiiii",employee_data)

	print("hchchchchchcg",data)
	total = sum([row.get('assigned') for row in data])
	print("total",total)
	completed = sum([row.get('completed') for row in data])
	print("completed",completed)
	overdue = sum([row.get('overdue') for row in data])
	print("overdue",overdue)
	working = sum([row.get('working') for row in data])
	print("working",working)
	
	completion_p = (completed / total) * 100 if total > 0 else 0
	overdue_p = (overdue / total) * 100 if total > 0 else 0
	working_p = (working / total) * 100 if total > 0 else 0

	summary = [
		{
			"value": completion_p,
			"indicator": "Green" if completion_p > 50 else "Red",
			"label": "Tasks Completion %",
			"datatype": "Percent",
		},
		{
			"value": overdue_p,
			"indicator": "Green" if overdue_p <= 10 else "Red",
			"label": "Tasks Overdue %",
			"datatype": "Percent",
		},
		{
			"value": working_p,
			"indicator": "Green" if working_p <= 20 else "Red",
			"label": "Tasks Working %",
			"datatype": "Percent",
		},
		{
			"value": total,
			"indicator": "Blue",
			"label": "Total Tasks",
			"datatype": "Int",
		},
		{
			"value": working,
			"indicator": "Orange",
			"label": "Working Tasks",
			"datatype": "Int",
		},
		{
			"value": completed,
			"indicator": "Green",
			"label": "Completed Tasks",
			"datatype": "Int",
		},
		{
			"value": overdue,
			"indicator": "Green" if overdue == 0 else "Red",
			"label": "Overdue Tasks",
			"datatype": "Int",
		}
	]

	if filters.get("include_issues") == 1:
		total_issues = sum([row.get('assigned_issues', 0) for row in data])
		completed_issues = sum([row.get('completed_issues', 0) for row in data])
		overdue_issues = sum([row.get('overdue_issues', 0) for row in data])
		working_issues = sum([row.get('working_issues', 0) for row in data])

		total += total_issues
		completed += completed_issues
		overdue += overdue_issues
		working += working_issues

		completion_p = (completed / total) * 100 if total > 0 else 0
		overdue_p = (overdue / total) * 100 if total > 0 else 0
		working_p = (working / total) * 100 if total > 0 else 0

		summary = [
			{
				"value": completion_p,
				"indicator": "Green" if completion_p > 50 else "Red",
				"label": "(Tasks + Issues) Completion %",
				"datatype": "Percent",
			},
			{
				"value": overdue_p,
				"indicator": "Green" if overdue_p <= 10 else "Red",
				"label": "(Tasks + Issues) Overdue %",
				"datatype": "Percent",
			},
			{
				"value": working_p,
				"indicator": "Green" if working_p <= 20 else "Red",
				"label": "(Tasks + Issues) Working %",
				"datatype": "Percent",
			},
			{
				"value": total,
				"indicator": "Blue",
				"label": "Total Tasks + Issues",
				"datatype": "Int",
			},
			{
				"value": working,
				"indicator": "Yellow",
				"label": "Working Tasks + Issues",
				"datatype": "Int",
			},
			{
				"value": completed,
				"indicator": "Green",
				"label": "Completed Tasks + Issues",
				"datatype": "Int",
			},
			{
				"value": overdue,
				"indicator": "Green" if overdue == 0 else "Red",
				"label": "Overdue Tasks + Issues",
				"datatype": "Int",
			}
		]

	return summary