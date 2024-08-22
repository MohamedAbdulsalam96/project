// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Team Utilization Summary"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1
        },
		{
            "fieldname": "project_type",
            "label": __("Project Type"),
            "fieldtype": "Link",
            "options": "Project Type",
        },
        {
            "fieldname": "employee_group",
            "label": __("Employee Group"),
            "fieldtype": "Link",
            "options":"Employee Group"
        },
		{
            "fieldname": "project_lead",
            "label": __("Project Lead"),
            "fieldtype": "Link",
            "options":"Employee"
        },
		{
            "fieldname": "primary_consultant",
            "label": __("Primary Consultant"),
            "fieldtype": "Link",
            "options":"Employee"
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Project", txt);
            }
        },
	]
};
