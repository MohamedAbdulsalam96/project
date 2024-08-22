from __future__ import unicode_literals
import frappe
from frappe import _



@frappe.whitelist()
def on_cancel_sales_order(doc, method):
    timesheets = frappe.get_all("Timesheet Detail", {"sales_order": doc.name},["name"])
    if timesheets:
        for t in timesheets:
            frappe.db.set_value("Timesheet Detail", t.get("name"), "sales_order", "")

    ra = frappe.get_all("Resource Allocation Items", {"sales_order": doc.name},["name"])
    if ra:
        for t in ra:
            frappe.db.set_value("Resource Allocation Items", t.get("name"), "sales_order", "")