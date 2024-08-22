# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe

def execute(filters):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": "Employee Group",
			"fieldname": "employee_group",
			"fieldtype": "Link",
			"options": "Employee Group",
			"width": 120
		},
		{
			"label": "Project Lead",
			"fieldname": "project_lead",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Project Lead Name",
			"fieldname": "project_lead_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Primary Consultant",
			"fieldname": "primary_consultant",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Primary Consultant Name",
			"fieldname": "primary_consultant_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Project",
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 120
		},
		{
			"label": "Project Name",
			"fieldname": "project_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Open Task Count",
			"fieldname": "open_task_count",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Overdue Task Count",
			"fieldname": "overdue_task_count",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Pending Milestones Count",
			"fieldname": "pending_milestones_count",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Allocation Hrs",
			"fieldname": "allocation_hrs",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": "Timesheet Hrs",
			"fieldname": "timesheet_hrs",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": "Project Count",
			"fieldname": "project_count",
			"fieldtype": "Float",
			"width": 120
		}
	]
	return columns

def get_data(filters):
    data = []
    conditions = []
    date_cond = []
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    if from_date and to_date:
        date_cond.append(f"t.exp_end_date BETWEEN '{from_date}' AND '{to_date}'")
        
    if filters.get("project"):
        project = filters.get("project")
        project_list = ", ".join([f"'{p}'" for p in project])
        conditions.append(f"p.name IN ({project_list})")

    if filters.get("project_type"):
        project_type = filters.get("project_type")
        conditions.append(f"p.project_type = '{project_type}'")

    if filters.get("employee_group"):
        employee_group = filters.get("employee_group")
        conditions.append(f"p.employee_group = '{employee_group}'")

    if filters.get("project_lead"):
        project_lead = filters.get("project_lead")
        conditions.append(f"p.project_lead = '{project_lead}'")

    if filters.get("primary_consultant"):
        primary_consultant = filters.get("primary_consultant")
        conditions.append(f"p.primary_consultant = '{primary_consultant}'")

    conditions_str = " AND ".join(conditions) if conditions else "1=1"
    date_data = " AND ".join(date_cond) if date_cond else "1=1"
    
    employee_group_query = f"""
        SELECT
            p.employee_group AS employee_group,
            COUNT(DISTINCT p.name) AS project_count,
            SUM((SELECT COUNT(*) FROM `tabTask` t WHERE t.project = p.name AND t.status NOT IN ('Cancelled', 'Completed', 'Overdue') AND t.exp_end_date BETWEEN '{from_date}' AND '{to_date}') and t.primary_consultant = p.primary_consultant) AS open_task_count,
            SUM((SELECT COUNT(*) FROM `tabTask` t WHERE t.project = p.name AND t.status = 'Overdue' AND t.exp_end_date BETWEEN '{from_date}' AND '{to_date}')) AS overdue_task_count,
            SUM((SELECT COUNT(*) FROM `tabMilestone Sign Off` m WHERE m.project = p.name AND m.status1 != 'Signed')) AS pending_milestones_count,
            SUM((SELECT SUM(t.duration_per_day_in_hours) FROM `tabTask` t WHERE t.project = p.name)) AS allocation_hrs,
            SUM((SELECT SUM(ts.total_hours) FROM `tabTimesheet` ts LEFT JOIN `tabTimesheet Detail` td ON td.parent = ts.name WHERE td.task IN (SELECT t.name FROM `tabTask` t WHERE t.project = p.name))) AS timesheet_hrs
        FROM
            `tabProject` p 
            LEFT JOIN `tabTask` t ON t.project = p.name
            JOIN `tabEmployee Group` eg ON eg.name = p.employee_group
            JOIN `tabEmployee` e ON e.employee_name = eg.group_lead_name
        WHERE
            {conditions_str} AND {date_data} AND e.status = 'Active' AND eg.custom_disabled = 0
        GROUP BY
            p.employee_group
    """

    employee_group_result = frappe.db.sql(employee_group_query, as_dict=True)
    print("**8***first print ****8>>>>>>>>>> ",employee_group_result)
    for eg_row in employee_group_result:
        eg_row['indent'] = 0.0
        data.append(eg_row)

        project_lead_query = f"""
            SELECT
                p.project_lead AS project_lead,
                p.project_lead_name,
                COUNT(DISTINCT p.name) AS project_count,
                SUM((SELECT COUNT(*) FROM `tabTask` t WHERE t.project = p.name AND t.status NOT IN ('Cancelled', 'Completed', 'Overdue') AND t.exp_end_date BETWEEN '{from_date}' AND '{to_date}' and t.primary_consultant = p.primary_consultant)) AS open_task_count,
                SUM((SELECT COUNT(*) FROM `tabTask` t WHERE t.project = p.name AND t.status = 'Overdue' AND t.exp_end_date BETWEEN '{from_date}' AND '{to_date}' )) AS overdue_task_count,
                SUM((SELECT COUNT(*) FROM `tabMilestone Sign Off` m WHERE m.project = p.name AND m.status1 != 'Signed')) AS pending_milestones_count,
                SUM((SELECT SUM(t.duration_per_day_in_hours) FROM `tabTask` t WHERE t.project = p.name)) AS allocation_hrs,
                SUM((SELECT SUM(ts.total_hours) FROM `tabTimesheet` ts LEFT JOIN `tabTimesheet Detail` td ON td.parent = ts.name WHERE td.task IN (SELECT t.name FROM `tabTask` t WHERE t.project = p.name))) AS timesheet_hrs
            FROM
                `tabProject` p
                
                JOIN `tabEmployee` e ON e.employee_name = p.project_lead_name
            WHERE
                {conditions_str}  AND p.is_active = 'Yes' AND e.status = 'Active'
                AND p.employee_group = "{eg_row["employee_group"]}"
            GROUP BY
                p.project_lead
        """
        
        project_lead_result = frappe.db.sql(project_lead_query, as_dict=True)
        print("**8***second print ****8 ",project_lead_result)
        total_project_count=0
        for pl_row in project_lead_result:
            
            pl_row['indent'] = 1.0
            pl_row['employee_group'] = ''
            total_project_count+=pl_row.get("project_count")
            eg_row.update({"project_count":total_project_count})

            data.append(pl_row)

            primary_consultant_query = f"""
                SELECT
                    p.primary_consultant,
                    p.primary_consultant_name,
                    p.name AS project,
                    p.project_name,
                    (SELECT COUNT(*) FROM `tabTask` t WHERE t.project = p.name AND t.status NOT IN ('Cancelled', 'Completed', 'Overdue') AND t.exp_end_date BETWEEN '{from_date}' AND '{to_date}' AND t.primary_consultant = p.primary_consultant) AS open_task_count,
                    (SELECT COUNT(*) FROM `tabTask` t WHERE t.project = p.name AND t.status = 'Overdue' AND t.exp_end_date BETWEEN '{from_date}' AND '{to_date}') AS overdue_task_count,
                    (SELECT COUNT(*) FROM `tabMilestone Sign Off` m WHERE m.project = p.name AND m.status1 != 'Signed') AS pending_milestones_count,
                    (SELECT SUM(t.duration_per_day_in_hours) FROM `tabTask` t WHERE t.project = p.name) AS allocation_hrs,
                    (SELECT SUM(ts.total_hours) FROM `tabTimesheet` ts LEFT JOIN `tabTimesheet Detail` td ON td.parent = ts.name WHERE td.task IN (SELECT t.name FROM `tabTask` t WHERE t.project = p.name)) AS timesheet_hrs
                FROM
                    `tabProject` p
                    
                    JOIN `tabEmployee` e ON e.employee_name = p.primary_consultant_name
                WHERE
                    {conditions_str} AND p.is_active = 'Yes' AND e.status = 'Active'
                    AND p.project_lead = "{pl_row["project_lead"]}"
                    AND p.employee_group = "{eg_row["employee_group"]}"
                
            """

            primary_consultant_result = frappe.db.sql(primary_consultant_query, as_dict=True)
            # print("**8***third print ****8 ",primary_consultant_result)

            for pc_row in primary_consultant_result:
                pc_row['indent'] = 2.0
                pc_row['project_lead'] = ''

                data.append(pc_row)
        
                
    return data