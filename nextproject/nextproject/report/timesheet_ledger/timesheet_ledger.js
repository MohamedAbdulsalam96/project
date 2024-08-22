// Copyright (c) 2022, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Timesheet Ledger"] = {
	"filters": [
		{
			"fieldname":"company",
			"label":__("Company"),
			"fieldtype":"Link",
			"options": "Company",
			"reqd":1,
            "default": frappe.defaults.get_user_default("company")
		},
		{
			"fieldname":"from_time",
			"label":__("From Date"),
			"fieldtype":"Date",
			"reqd":1,
			"default":frappe.datetime.add_months(frappe.datetime.get_today(), -1),		
		},
		{
			"fieldname":"to_time",
			"label":__("To Date"),
			"fieldtype":"Date",
			"reqd":1,
			"default": frappe.datetime.get_today()	
		},
		{
			"fieldname":"project",
			"label":__("Project"),
			"fieldtype":"Link",
			"options":"Project"
		},
		{
			"fieldname":"employee",
			"label":__("Employee"),
			"fieldtype":"Link",
			"options":"Employee"
		},
		{
			"fieldname":"task",
			"label":__("Task"),
			"fieldtype":"Link",
			"options":"Task"
		},
		{
			"fieldname":"sales_invoice",
			"label":__("Sales Invoice"),
			"fieldtype":"Link",
			"options":"Sales Invoice"
		},
		{
			"fieldname":"is_billable",
			"label":__("Is Billable"),
			"fieldtype":"Check"
		}


	]
};
