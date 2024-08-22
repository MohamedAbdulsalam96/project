// Copyright (c) 2022, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Status"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": ("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd":1
		},
		{
			"fieldname":"employee_group",
			"label": ("Employee Group"),
			"fieldtype": "Link",
			"options": "Employee Group"

			
		},
		{
			"fieldname":"primary_consultant",
			"label": ("Primary Consultant"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname":"project",
			"label": ("Project"),
			"fieldtype": "Link",
			"options": "Project"
		}

		

	]
};
