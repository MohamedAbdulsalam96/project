from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def on_cancel_sales_invoice(doc, method):
    timesheets = frappe.get_all("Timesheet Detail", {"sales_invoice": doc.name},["name"])
    if timesheets:
        for t in timesheets:
            frappe.db.set_value("Timesheet Detail", t.get("name"), "sales_invoice", "")


    ra = frappe.get_all("Resource Allocation Items", {"sales_invoice": doc.name},["name"])
    if ra:
        for t in ra:
            frappe.db.set_value("Resource Allocation Items", t.get("name"), "sales_invoice", "") # for ex_name in SI.items:
        # if not ex_name:
        #     print("Expens
def check_expense(doc,method):
    print("ggggggggggggggggggggggggg")
    for i in doc.items:
        if i.expense_claim:
            expe_claim = frappe.get_doc("Expense Claim", i.expense_claim)
            print("==================",i)
            for item in doc.items:
                if item.expense_claim == expe_claim.name:
                    print("kkkkkkkkkkkkkkkkk",item.expense_claim,i.name)
                    expe_claim.db_set("sales_invoice_created",  1)
                # expe_claim.save(ignore_permissions=True)

def cancel_expense(doc,method):
    print("ggggggggggggggggggggggggg")
    for i in doc.items:
        if i.expense_claim: 
            expe_claim = frappe.get_doc("Expense Claim", i.expense_claim)
            print("==================",i)
            for item in doc.items:
                if item.expense_claim == expe_claim.name:
                    print("kkkkkkkkkkkkkkkkk",item.expense_claim,i.name)
                    expe_claim.db_set("sales_invoice_created",  0)
                    # expe_claim.save(ignore_permissions=True)
def before_cancel(doc,method):
    print("ggggggggggggggggggggggggg")
    for i in doc.items:
        if i.expense_claim:
            value=frappe.db.sql("""select parent
                                    from `tabSales Invoice Item` 
                                    where expense_claim='{0}' and docstatus=1 limit 1
                                    """.format(i.expense_claim),as_dict=1)
            if value:
                frappe.throw("Sales Invoice {0} already present from same expense claim {1}".format(value[0].get("parent"),i.expense_claim))
        
