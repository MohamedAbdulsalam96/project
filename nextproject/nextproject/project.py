from __future__ import unicode_literals
import json
from erpnext.projects.doctype.project.project import Project
import frappe
from frappe import _
from frappe.utils.data import flt

class CustomProject(Project):
    def get_print_settings(self):
        print_setting_fields = []
        
        print_setting_fields += ["hide_group_tasks","hide_com_task","show_billable_only"]

        return print_setting_fields



@frappe.whitelist()
def sales_order_naming_series():
    series = frappe.get_meta("Sales Order").get_field("naming_series").options.strip().split("\n")
    print(series)
    return series

@frappe.whitelist()
def update_task(values,project):
    frappe.enqueue(
			"nextproject.nextproject.project.background_task_update",
			values=values,
			project=project,
			timeout=10000,
		)
    frappe.msgprint("The task has been enqueued as a background job. In case there is any issue on processing in background, the system will add a comment")




def background_task_update(values,project):
    values=json.loads(values)
    doc1=frappe.get_all("Task",{"status":["in",["Open","Working","Pending Review","Overdue"]],"project":project},["name"])
    for t in doc1:
        try:
            doc2=frappe.get_doc("Task",t.name)
            doc2.db_set("company",values.get("company"))
            doc2.db_set("primary_consultant",values.get("primary_consultant"))
            doc2.db_set("project_lead",values.get("project_lead"))
            doc2.db_set("employee_group",values.get("employee_group"))
            doc2.db_set("department",values.get("department"))
            frappe.db.commit()
        except:
            doc=frappe.get_doc("Task",t.name)
            traceback = frappe.get_traceback()
            doc.add_comment("Error", traceback)

@frappe.whitelist()
def sales_invoice_naming_series():
    series = frappe.get_meta("Sales Invoice").get_field("naming_series").options.strip().split("\n")
    print(series)
    return series

@frappe.whitelist()
def get_contacts(name):
    contacts = {}
    cnp = []
    cp =[]
    eids = frappe.db.sql("""
                         select  ect2.email_id  as pe, ect.email_id as npe from `tabContact` ct
                         join `tabDynamic Link` dl on dl.link_name = '{0}' and dl.parent = ct.name
                         join `tabContact Email` ect on ect.parent = ct.name and ect.is_primary = 0
                         join `tabContact Email` ect2 on ect2.parent = ct.name and ect2.is_primary = 1
                            """.format(name),as_dict=1)
    if eids:
        for emails in eids:
            cnp.append(emails.get("npe"))
            cp.append(emails.get("pe"))
        
        contacts.update({
            "primary":set(cp),
            "nprimary":set(cnp)
        })
        

        print("sjnv  v**********************",contacts)
        return contacts

def proj_active(self,method):
    if self.is_active=="No":
        doc1=frappe.get_all("Task",{"status":["in",["Open","Working","Pending Review","Overdue"]],"project":self.name},["name"])
        for t in doc1:
            doc2=frappe.get_doc("Task",t.name)
            doc2.db_set("status", "Cancelled")





@frappe.whitelist()
def get_expense_claim(values,name):
    print("kkkkkkkkkkkkkkkkk",values)
    a=json.loads(values)
    result = frappe.db.sql("""select name
                                    from `tabExpense Claim` 
                                    where project = '{0}' and posting_date between '{1}' and '{2}' and sales_invoice_created = 0
                                    """.format(a.get("project"),a.get("from_date"),a.get("to_date")), as_dict=True)
    
    print("lllllllllllllllllllllllllll",result)

    claim=frappe.get_doc("Expense Claim",{"project":name})
    b=frappe.get_doc("Project",a.get("project"),a.get("customer"))
    print("==============================",b)


    if claim.sales_invoice_created != 1:
    

        SI = frappe.new_doc("Sales Invoice")
        for exp in result:
            print("777777777777777",exp.name)
            
            
            ec= frappe.get_doc("Expense Claim",exp.name)
            for ex_type in ec.expenses:
                account=frappe.get_doc("Expense Claim Type",{"name":ex_type.expense_type})
                ect_child =frappe.get_doc("Expense Claim Account",{"parent":account.name})
                print("!!!!!!!!!!!!!!!!!!!!!!",ect_child.income_account)
            if ec.status == "Paid" or ec.status =="Unpaid":
                SI.naming_series = b.sales_invoice_naming_series
                SI.customer = b.customer
                SI.company = b.company
                SI.cost_center = ec.cost_center
                SI.currency = b.currency
                SI.due_date = frappe.utils.nowdate()
                SI.project = b.name
                SI.sales_taxes_charges_template=b.total_sales_amount
                SI.tc_name=b.terms
                if b.price_list:
                    SI.selling_price_list=b.total_billed_amount
                if not exp.price_list and b.customer:
                    doc=frappe.get_doc("Customer",b.customer)
                    if doc.default_price_list:
                        SI.selling_price_list=doc.default_price_list
                # if prj=="Sales Invoice":
                SI.remarks="Project Code :"+str(b.name)+"\n Project Name :"+str(b.project_name)+"\n Billing Type :"+str(b.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(b.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                for exp_type in ec.expenses:
                    books=exp_type.expense_type
                    print("**************************",books)
                    if not ect_child.income_account:
                        frappe.throw("Income account not found")
                    SI.append("items", {
                        "expense_claim":exp.name,
                        "item_name": exp_type.expense_type,
                        "qty": 1,
                        "rate":exp_type.amount,
                        "uom" : "Hour",
                        "description": """{0} <br> {1}""".format(ec.get_formatted("posting_date"), books),
                        "income_account":ect_child.income_account,
                        "conversion_factor": 1,
                    })
                print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",SI)
                if b.sales_taxes_charges_template:
                    tax=frappe.get_doc("Sales Taxes and Charges Template",b.sales_taxes_charges_template)
                    for i in tax.taxes:
                        SI.append("taxes", {
                            "charge_type": i.charge_type,
                            "description":i.description,
                            "account_head": i.account_head,
                            "rate": i.rate
                        })
                if b.terms:
                    term=frappe.get_doc("Terms and Conditions",b.terms)
                    SI.terms=term.terms
                    SI.validate()
                    SI.insert(ignore_permissions=True)
                # else:
                #     frappe.throw("not found")
                # if exp=="Sales Invoice":
                    # SI.posting_date=b.expected_start_date

        SI.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint("successfully created sales invoice")
    else:
        frappe.throw("Sales Invoice already  created")
