from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields




def execute():

    create_custom_fields(
    {
        "Print Settings": [
            {
                "label": _("Show Billable Only"),
                "fieldname": "show_billable_only",
                "fieldtype": "Check",
                "default": "1",
                "insert_after":"print_taxes_with_zero_amount"
            },
            {
                "label": _("Hide Completed Task"),
                "fieldname": "hide_com_task",
                "fieldtype": "Check",
                "default": "0",
                "insert_after": "show_billable_only"
            },
            {
                "label": _("Hide Group Tasks"),
                "fieldname": "hide_group_tasks",
                "fieldtype": "Check",
                "default": "0",
                "insert_after": "hide_com_task"
            },
        ]
    })