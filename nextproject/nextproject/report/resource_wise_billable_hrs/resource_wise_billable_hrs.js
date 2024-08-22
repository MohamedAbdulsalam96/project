// Copyright (c) 2016, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Resource Wise Billable Hrs"] = {
	"filters": [
//	    {
//			"fieldname":"from_date",
//			"label": __("From Date"),
//			"fieldtype": "Date",
//			"default": frappe.datetime.get_today(),
//			"reqd": 1,
//			"width": "60px"
//		},
//		{
//			"fieldname":"to_date",
//			"label": __("To Date"),
//			"fieldtype": "Date",
//			"default": frappe.datetime.get_today(),
//			"reqd": 1,
//			"width": "60px"
//		},
        {
			"fieldname":"period",
			"label": __("Period"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Daily", "label": __("Daily") },
				{ "value": "Monthly", "label": __("Monthly") }
				
			],
			"default": "Monthly"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"depends_on":"eval:doc.period == 'Daily'"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"depends_on":"eval:doc.period == 'Daily'"
		},
		{
			"fieldname":"based_on",
			"label": __("Based On"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Employee", "label": __("Employee") },
				{ "value": "Department", "label": __("Department") },
				{ "value": "Employee Group", "label": __("Employee Group") },
				{ "value": "Project", "label": __("Project") }
			],
			"default": "Employee",
			"dashboard_config": {
				"read_only": 1,
			}
		},
		{
			"fieldname":"group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": [
				"",
				{ "value": "Project", "label": __("Project") },
				{ "value": "Employee", "label": __("Employee") }
			],
			"default": ""
		},
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options":'Fiscal Year',
			"default": frappe.sys_defaults.fiscal_year,
			"depends_on":"eval:doc.period == 'Monthly'"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
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
//		{
//			fieldname:"department",
//			label: __("Department"),
//			fieldtype: "Link",
//			options: "Department"
//		},
		{
			fieldname:"billable",
			label: __("Billable"),
			fieldtype: "Check"
			
		
		}
	]
};