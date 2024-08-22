// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.query_reports["Under Utilized Resources"] = {
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
            "fieldname": "report_to",
            "label": __("Report To"),
            "fieldtype": "Link",
            "options":"Employee"
        },
        {
            "fieldname": "min_utilization",
            "label": __("Min Utilization %"),
            "fieldtype": "Percent",
            "default": 50,
            // "reqd": 1
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Employee", txt);
            }
        },
        {
            "fieldname": "periodicity",
            "label": __("Periodicity"),
            "fieldtype": "Select",
            "options": ["Daily", "Weekly", "Monthly"],
            "default": "Daily"
        },
        {
            "fieldname": "considred_completed_task",
            "label": __("Considered Completed Task"),
            "fieldtype": "Check"
        }
    ]
};