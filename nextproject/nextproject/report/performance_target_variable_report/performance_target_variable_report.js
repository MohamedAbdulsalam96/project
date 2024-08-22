// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Performance Target Variable Report"] = {
	
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
        },
	    
		{
			"fieldname":"fy",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			 get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				};
			},
			"reqd": 1,
			
		},
	     ,
	    {
			"fieldname":"emp",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			 get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				};
			}
		},
		// {
		// 	"fieldname":"from_date",
		// 	"label": __("From Date"),
		// 	"fieldtype": "Date",
		// 	"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		// 	"reqd": 1,
		// 	"width": "60px"
		// },
		// {
		// 	"fieldname":"to_date",
		// 	"label": __("To Date"),
		// 	"fieldtype": "Date",
		// 	"default": frappe.datetime.get_today(),
		// 	"reqd": 1,
		// 	"width": "60px"
		// },
		{
			"fieldname":"periodicity",
			"label": __("Periodicity"),
			"fieldtype": "Select",
			"options":['Monthly','Quatarly','Half Yearly','Yearly'],
			"default": 'Monthly',
		}
	],

};

