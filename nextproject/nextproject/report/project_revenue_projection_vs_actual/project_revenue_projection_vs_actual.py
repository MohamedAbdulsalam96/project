# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    print("**********data **************",data)
    chart = get_chart(data,filters) if data else None
    return columns, data, None, chart


def get_columns(filters):
    columns = [
        {
            "fieldname": "project",
            "label": "Project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 120
        },
        {
            "fieldname": "billing_based_on",
            "label": "Billing Based on",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "last_billing_date",
            "label": "Last Billing Date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "next_billing_date",
            "label": "Next Billing Date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "projected_costing_amount",
            "label": "Projected Costing Amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "projected_amount",
            "label": "Projected Amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "invoice_amount",
            "label": "Invoice Amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "sales_invoice",
            "label": "Sales Invoice",
            "fieldtype": "Link",
            "options" : "Sales Invoice",
            "width": 120
        },
        {
            "fieldname": "primary_consultant",
            "label": "Primary Consultant",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "fieldname": "task",
            "label": "Task",
            "fieldtype": "Link",
            "options": "Task",
            "width": 150
        },
        {
            "fieldname": "billing_rate",
            "label": "Billing Rate",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "fieldname": "costing_rate",
            "label": "Costing Rate",
            "fieldtype": "Currency",
            "width": 120
        }
    ]

    return columns


def get_data(filters):
    items = set()

    filters = filters or {}
    project_filter = filters.get("project")

    if project_filter:
        records = frappe.get_list("Project Revenue Projection", fields=["*"], filters=[
            ["project", '=', project_filter],
            ['last_billing_date', '>=', filters.get("from_date")],
            ['next_billing_date', '<=', filters.get("to_date")]
        ])
    else:
        records = frappe.get_list("Project Revenue Projection", fields=["*"], filters=[
            ['last_billing_date', '>=', filters.get("from_date")],
            ['next_billing_date', '<=', filters.get("to_date")]
        ])

    grouped_data = {}
    for record in records:
        # print("Record is  ",record)
        project = record.get("project")
        billing_based_on = record.get("billing_based_on")
        last_billing_date = record.get("last_billing_date")
        next_billing_date = record.get("next_billing_date")
        invoice_total_amount = record.get("invoiced_amount")
        projected_amount = record.get("projected_amount")
        sales_inv = record.get("sales_invoice") if record.get("sales_invoice") else None
        projected_costing_amount = record.get("projected_costing_amount")
        key = (project, billing_based_on, last_billing_date, next_billing_date, invoice_total_amount,projected_amount,projected_costing_amount)

        if key not in grouped_data:
            grouped_data[key] = {
                "project": project,
                "billing_based_on": billing_based_on,
                "last_billing_date": last_billing_date,
                "next_billing_date": next_billing_date,
                "invoice_amount": invoice_total_amount,
                "projected_amount" : projected_amount,
                "sales_invoice" : sales_inv,
                "projected_costing_amount" : projected_costing_amount,  
                "consultants": []
            }

        # Fetching consultant details from child table
        consultant_records = frappe.get_all('Project Revenue Projection Items',
                                            filters={'parent': record.get('name')},
                                            fields=['primary_consultant', 'task', 'hours', 'costing_rate', 'cost_amount', 'billing_rate', 'bill_amount'])
        for consultant in consultant_records:
            grouped_data[key]['consultants'].append({
                "primary_consultant_name": consultant.get("primary_consultant"),
                "task": consultant.get("task"),
                "hours": consultant.get("hours"),
                "costing_rate": consultant.get("costing_rate"),
                "cost_amount": consultant.get("cost_amount"),
                "billing_rate": consultant.get("billing_rate"),
                "bill_amount": consultant.get("bill_amount")
            })

    data = []
    last_main_key = None
    for key, value in grouped_data.items():
        current_main_key = key[:6]  

        if last_main_key is None or last_main_key != current_main_key:
            data.append({
                "project": value["project"],
                "billing_based_on": value["billing_based_on"],
                "last_billing_date": value["last_billing_date"],
                "next_billing_date": value["next_billing_date"],
                "invoice_amount": value["invoice_amount"],
                "sales_invoice" : value["sales_invoice"],
                "projected_amount" : value["projected_amount"],
                "projected_costing_amount" : value["projected_costing_amount"],  
                "indent": 0
            })

            for consultant in value["consultants"]:
                data.append({
                    "project": "",
                    "billing_based_on": "",
                    "last_billing_date": "",
                    "next_billing_date": "",
                    "invoice_amount": "",
                    "projected_amount" : "",
                    "sales_invoice" : "",
                    "projected_costing_amount" : "",  
                    "indent": 1,
                    "primary_consultant": consultant["primary_consultant_name"],
                    "task": consultant["task"],
                    "hours": consultant["hours"],
                    "costing_rate": consultant["costing_rate"],
                    "cost_amount": consultant["cost_amount"],
                    "billing_rate": consultant["billing_rate"],
                    "bill_amount": consultant["bill_amount"],
                })

        last_main_key = current_main_key

    return data


def get_chart(data, filters):
    labels = []
    projected_amounts = []
    invoice_amounts = []

    # Collect project-wise data
    for record in data:
        if record.get("indent") == 0:  # Main project data
            labels.append(record.get("project"))
            projected_amounts.append(record.get("projected_amount"))
            invoice_amounts.append(record.get("invoice_amount"))

    chart = {
        "type": "bar",
        "data": {
            "labels": labels, 
            "datasets": [
                {
                    "name": "Projected Amount", 
                    "values": projected_amounts
                },
                {
                    "name": "Invoice Amount", 
                    "values": invoice_amounts
                }
            ]
        },
        "colors": ["#7cd6fd", "#743ee2"],
        "title": "Project Revenue Metrics",
        "x_axis_label": "Project",
        "y_axis_label": "Amount"
    }

    return chart