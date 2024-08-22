# Assuming you have a Frappe API endpoint to handle signature saving
import frappe
@frappe.whitelist(allow_guest=True)
def save_signature(signature,task_name):
    all_mile_doc = frappe.get_all('Milestone Sign Off')
    for rec in all_mile_doc:

        doc = frappe.get_doc('Milestone Sign Off',rec.name)
        for i in doc.milestone_depends_on_task:
            if i.task == task_name:
                i.signature = signature
                i.sign = signature
                i.save(ignore_permissions=True)
    return "Signature saved successfully"
