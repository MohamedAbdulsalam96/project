// Copyright (c) 2016, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Resource wise Project Allocation"] = {
	"filters": [
        {
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd":1
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"reqd":1,
			"default":frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},

		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"reqd":1,
			"default":frappe.datetime.get_today()
		},
        {
			fieldname:"project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project"
		},
		{
			fieldname:"employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee"
		},
        {
			fieldname:"department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department"
		},
		{
			fieldname:"billable",
			label: __("Billable"),
			fieldtype: "Check"
		},
		{
			fieldname:"project_wise_resource",
			label: __("Project Wise Resource"),
			fieldtype: "Check"
		},
		{
			fieldname:"show_active",
			label: __("Show Active Employees"),
			fieldtype: "Check"
		},
		{
			fieldname:"show_open_projects",
			label: __("Show Open Projects"),
			fieldtype: "Check",
			default: 1
		}
	]
};