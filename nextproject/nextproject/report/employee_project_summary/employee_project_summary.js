// Copyright (c) 2022, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Project Summary"] = {
	"filters": [
		{
			"fieldname":"based_on",
			"label": ("Based On"),
			"fieldtype": "Select",
			"reqd":1,
			"options": ["","Team Lead","Primary Consultant","Department","Employee Group"],
			"default": 'Team Lead'
			
		},
		{
			"fieldname":"group_by",
			"label": ("Group By"),
			"fieldtype": "Select",
			"options": ["","Project"]
		},
		{
			"fieldname":"include_issues",
			"label": ("Include Issues"),
			"fieldtype": "Check",
		},
		{
			"fieldname":"team_lead",
			"label": ("Team Lead"),
			"fieldtype": "MultiSelectList",
			// "options": "Employee",
			"depends_on": "eval:doc.based_on == 'Team Lead'",
			"get_data": function(txt) {
                return frappe.db.get_link_options("Employee", txt ,{
                    status: 'Active'});
            }
			
			
		},
		{
			"fieldname":"primary_consultant",
			"label": ("Primary Consultant"),
			"fieldtype": "MultiSelectList",
			// "options": "Employee",
			"depends_on": "eval:doc.based_on == 'Primary Consultant'",
			"get_data": function(txt) {
                return frappe.db.get_link_options("Employee", txt ,{
                    status: 'Active'});
            }
			
			
		},
		{
			"fieldname":"department",
			"label": ("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"depends_on": "eval:doc.based_on == 'Department'"
			
			
		},
		{
			"fieldname":"employee_group",
			"label": ("Employee Group"),
			"fieldtype": "MultiSelectList",
			"depends_on": "eval:doc.based_on == 'Employee Group'",
			"get_data": function(txt) {
                return frappe.db.get_link_options("Employee Group", txt);
            }
			
			
		},
		{
			"fieldname":"project",
			"label": ("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"depends_on": "eval:doc.group_by == 'Project'"
			
			
		},
		
		
		
		

	],
	
	
	
};
