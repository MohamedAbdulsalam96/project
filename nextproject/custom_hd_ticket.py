import frappe
@frappe.whitelist()
def get_linked_tasks(doc):
    tasks = frappe.get_all('Task', filters={'subject': doc}, fields=['name', 'status', 'primary_consultant_name','exp_end_date','expected_time'],
    ignore_permissions=True)
    return tasks