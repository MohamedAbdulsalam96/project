import frappe
from nextproject.patch_task import cal_dt

def execute():
    frappe.reload_doc("projects","doctype","task")
    cal_dt()
