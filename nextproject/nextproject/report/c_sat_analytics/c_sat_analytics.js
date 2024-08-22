// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt


frappe.query_reports["C-SAT Analytics"] = {
	"filters": [
		{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
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
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Customer", txt);
            }
        },
		{
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Project", txt);
            }
        },
        {
            "fieldname": "periodicity",
            "label": __("Periodicity"),
            "fieldtype": "Select",
            "options": ["Monthly", "Quarterly", "Half-Yearly","Yearly"],
            "default": "Monthly"
        },
		{
            "fieldname": "based_on",
            "label": __("Based on"),
            "fieldtype": "Select",
            "options": ["C-SAT Form", "Question", "Customer","Project","Project Lead","Primary Consultant","Department","Customer City","Customer State","Customer Country"],
            "default": "C-SAT Form"
        },

		
	]
};
