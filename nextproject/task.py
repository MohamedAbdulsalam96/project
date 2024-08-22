
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (flt, getdate, get_url, now,
                          nowtime, get_time, today, get_datetime, add_days, datetime)
from erpnext.controllers.queries import get_filters_cond
from frappe.desk.reportview import get_match_cond
#from erpnext.hr.doctype.daily_work_summary.daily_work_summary import get_users_email
#from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils.data import add_to_date, date_diff



# frappe.whitelist()
def validate_issue(self, method):
    validate_estimate_time(self)

    if self.issue:
        doc=frappe.get_doc('Issue',self.issue) 
        doc.task_created=1
        doc.save(ignore_permissions=1)


    if self.status=="Completed":
        timesheet=frappe.db.get_all("Timesheet Detail",{"task":self.name,"docstatus":0},["name"])
        if timesheet:
            frappe.throw("Please Submit All Timesheet Where Task '{0}'".format(self.name))


    if self.status=="Completed":
        if self.project:
            project=frappe.get_doc("Project",self.project)
            if project.billing_based_on =='Milestone Based':
                for i in project.milestone:
                    if i.milestone==self.name:
                        i.progress=100
                        project.save(ignore_permissions=True)

  


@frappe.whitelist()
def daily():

    # for billing based on milestone
    project = frappe.db.sql(""" select name from `tabProject`
                                where billing_based_on = 'Milestone Based' and status = "Open" and is_active="Yes"
                                """,
                                as_dict= True)

    for proj in project:
        Prj = frappe.get_doc("Project",proj['name'])
        doctype = Prj.auto_creation_doctype
        SI = frappe.new_doc(doctype)
        if doctype == "Sales Order":
            SI.naming_series = Prj.sales_order_naming_series
            SI.delivery_date = frappe.utils.nowdate()
        if doctype == "Sales Invoice":
            SI.naming_series = Prj.sales_invoice_naming_series
        SI.customer = Prj.customer
        SI.currency = Prj.currency
        SI.due_date = frappe.utils.nowdate()
        SI.company = Prj.company

        SI.project = Prj.name
        SI.taxes_and_charges=Prj.sales_taxes_charges_template
        SI.tc_name=Prj.terms
        
        SI.letter_head=frappe.db.get_value("Company",{"name":Prj.company},["default_letter_head"])
        if Prj.price_list:
            SI.selling_price_list=Prj.price_list
        if not Prj.price_list and Prj.customer:
            doc=frappe.get_doc("Customer",Prj.customer)
            if doc.default_price_list:
                SI.selling_price_list=doc.default_price_list
            
        project_list_task = frappe.db.sql(""" select milestone,billing_item,billing_percentage from `tabProject Milestone Child` 
                                            where progress = 100 and parent = %(proj)s 
                                            and (COALESCE(invoice,'')='' and COALESCE(s_order,'')='')""",{'proj':proj['name']},as_dict=True)
        company=frappe.get_doc("Company",Prj.company)
        SI.cost_center=Prj.cost_center if Prj.cost_center else company.cost_center,
        for task in project_list_task:
            if Prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(Prj.name)+"\n Project Name :"+str(Prj.project_name)+"\n Billing Type : Milestone Bill"+"\n Milestone Name :"+str(task["milestone"])
                SI.append("items", {
                    "item_code": task["billing_item"],
                    "qty": 1,
                    "cost_center":Prj.cost_center if Prj.cost_center else company.cost_center,
                    "uom":Prj.custom_uom,
                    "project":Prj.name,
                    "rate": ((Prj.total_project_value_excluding_taxes * task["billing_percentage"]) / 100),
                    "conversion_factor": 1,
                })
            if Prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": task["billing_item"],
                    "description":"Project Code :"+str(Prj.name)+"\n Project Name :"+str(Prj.project_name)+"\n Billing Type : Milestone Bill"+"\n Milestone Name :"+str(task["milestone"]),
                    "qty": 1,
                    "uom":Prj.custom_uom,
                    "project":Prj.name,
                    "cost_center":Prj.cost_center if Prj.cost_center else company.cost_center,
                    "rate": ((Prj.total_project_value_excluding_taxes * task["billing_percentage"]) / 100),
                    "conversion_factor": 1,
                })
            if Prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",Prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if Prj.terms:
                term=frappe.get_doc("Terms and Conditions",Prj.terms)
                SI.terms=term.terms
            if task.milestone:
                SI.insert(ignore_permissions=True)
                SI.save(ignore_permissions=True)
                if Prj.auto_creation_doctype=="Sales Order":
                    Prj.start_date=SI.transaction_date
                if Prj.auto_creation_doctype=="Sales Invoice":
                    Prj.start_date=SI.posting_date
                Prj.save(ignore_permissions=True)
                if doctype == "Sales Order":
                    frappe.db.sql(""" update `tabProject Milestone Child` set s_order = %(name)s where parent = %(parent)s""",
                                {'name': SI.name, 'parent': Prj.name})
                    frappe.db.commit()
                if doctype == "Sales Invoice":
                    frappe.db.sql(""" update `tabProject Milestone Child` set invoice = %(name)s where parent = %(parent)s""",
                                {'name': SI.name, 'parent': Prj.name})
                    frappe.db.commit()
                if Prj.auto_submit_invoice == 1 or Prj.auto_submit_order == 1:
                    SI.submit()


   # for biiling based on fixed recurring

    recc_project = frappe.db.sql(""" select name from `tabProject`
                                    where billing_based_on = 'Fixed Recurring' and status = "Open" and is_active="Yes"  and  custom_to_be_billed_in_advance=0
                                    """,as_dict=True)
    for proj in recc_project:
        prj = frappe.get_doc("Project", proj['name'])
        if prj.billing_frequency == "Daily":
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = prj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = prj.sales_invoice_naming_series
            SI.customer = prj.customer
            SI.company = prj.company

            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.taxes_and_charges=prj.sales_taxes_charges_template
            SI.tc_name=prj.terms
            SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])
            
            if prj.price_list:
                SI.selling_price_list=prj.price_list
            if not prj.price_list and prj.customer:
                doc=frappe.get_doc("Customer",prj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center,
            if prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if prj.terms:
                term=frappe.get_doc("Terms and Conditions",prj.terms)
                SI.terms=term.terms
            # SI.validate()
            SI.insert(ignore_permissions=True)
            if prj.auto_creation_doctype=="Sales Order":
                prj.start_date=SI.transaction_date
            if prj.auto_creation_doctype=="Sales Invoice":
                prj.start_date=SI.posting_date
            prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                              {'date': frappe.utils.nowdate(), 'name': prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                              {'date': frappe.utils.nowdate(), 'name': prj.name})
                frappe.db.commit()
            if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                SI.submit()


        delta = getdate(frappe.utils.nowdate()) - prj.start_date
        if prj.billing_frequency == "Weekly" and int(delta.days) >= 7 or prj.billing_frequency == "Monthly" and int(delta.days) >= 30 or prj.billing_frequency == "Quaterly" and int(
            delta.days) >= 90 or prj.billing_frequency == "Bi-Yearly" and int(delta.days) >= 180 or prj.billing_frequency == "Yearly" and int(delta.days) >= 360:
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = prj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = prj.sales_invoice_naming_series
            SI.customer = prj.customer
            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.company = prj.company
            SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])

            SI.taxes_and_charges=prj.sales_taxes_charges_template
            SI.tc_name=prj.terms
            if prj.price_list:
                SI.selling_price_list=prj.price_list
            if not prj.price_list and prj.customer:
                doc=frappe.get_doc("Customer",prj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center
            if prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n [YYYY-MM-DD]"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n [YYYY-MM-DD]",
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "qty": 1,
                   "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n [YYYY-MM-DD]"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n[YYYY-MM-DD]",
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if prj.terms:
                term=frappe.get_doc("Terms and Conditions",prj.terms)
                SI.terms=term.terms
            # SI.validate()
            SI.insert(ignore_permissions=True)
           
            if prj.auto_creation_doctype=="Sales Order":
                prj.start_date=SI.transaction_date
            if prj.auto_creation_doctype=="Sales Invoice":
                prj.start_date=SI.posting_date
            prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                              {'date': frappe.utils.nowdate(), 'name': prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                              {'date': frappe.utils.nowdate(), 'name': prj.name})
                frappe.db.commit()
            if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                SI.submit()


        if prj.billing_frequency == "Custom":
            delta = frappe.utils.nowdate()
            lst = delta.split("-")
            exact_date = lst[2]
            specified_dates = frappe.db.sql(""" select day_number from `tabTimesheet Days` where parent=%(name)s """,{'name':prj.name},as_dict=1)
            for days in specified_dates:
                if days['day_number'] == int(exact_date):
                    doctype = prj.auto_creation_doctype
                    SI = frappe.new_doc(doctype)
                    if doctype == "Sales Order":
                        SI.naming_series = prj.sales_order_naming_series
                        SI.delivery_date = frappe.utils.nowdate()
                    if doctype == "Sales Invoice":
                        SI.naming_series = prj.sales_invoice_naming_series
                    SI.customer = prj.customer
                    SI.currency = prj.currency
                    SI.due_date = frappe.utils.nowdate()
                    SI.project = prj.name
                    SI.company = prj.company
                    SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])


                    SI.taxes_and_charges=prj.sales_taxes_charges_template
                    SI.tc_name=prj.terms
                    if prj.price_list:
                        SI.selling_price_list=prj.price_list
                    if not prj.price_list and prj.customer:
                        doc=frappe.get_doc("Customer",prj.customer)
                        if doc.default_price_list:
                            SI.selling_price_list=doc.default_price_list
                    company=frappe.get_doc("Company",prj.company)
                    SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center
                    if prj.auto_creation_doctype=="Sales Invoice":
                        SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                        SI.append("items", {
                            "item_code": prj.recurring_item,
                            "qty": 1,
                            "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                            "uom":prj.custom_uom,
                            "project":prj.name,
                            "rate": prj.recurring_charges,
                            "conversion_factor": 1,
                        })
                    if prj.auto_creation_doctype=="Sales Order":
                        SI.append("items", {
                            "item_code": prj.recurring_item,
                            "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                            "qty": 1,
                            "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                            "uom":prj.custom_uom,
                            "project":prj.name,
                            "rate": prj.recurring_charges,
                            "conversion_factor": 1,
                        })
                    if prj.sales_taxes_charges_template:
                        tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                        for i in tax.taxes:
                            SI.append("taxes", {
                                "charge_type": i.charge_type,
                                "description":i.description,
                                "account_head": i.account_head,
                                "rate": i.rate
                            })
                    if prj.terms:
                        term=frappe.get_doc("Terms and Conditions",prj.terms)
                        SI.terms=term.terms
                    # SI.validate()
                    SI.insert(ignore_permissions=True)
                    
                    if prj.auto_creation_doctype=="Sales Order":
                        prj.start_date=SI.transaction_date
                    if prj.auto_creation_doctype=="Sales Invoice":
                        prj.start_date=SI.posting_date
                    prj.save(ignore_permissions=True)
                    if doctype == "Sales Order":
                        frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                                      {'date': frappe.utils.nowdate(), 'name': prj.name})
                        frappe.db.commit()
                    if doctype == "Sales Invoice":
                        frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                                      {'date': frappe.utils.nowdate(), 'name': prj.name})
                        frappe.db.commit()
                    if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                        SI.submit()

                    break

# for Advance biiling based on fixed recurring
    recc_project = frappe.db.sql(""" select name from `tabProject`
                                    where billing_based_on = 'Fixed Recurring' and status = "Open" and is_active="Yes" and custom_to_be_billed_in_advance=1
                                    """,as_dict=True)
    for proj in recc_project:
        prj = frappe.get_doc("Project", proj['name'])
        if prj.billing_frequency == "Daily" and getdate(frappe.utils.nowdate())>getdate(prj.start_date):
            advance_bill_until=getdate(prj.start_date)+timedelta(days=1)
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = prj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = prj.sales_invoice_naming_series
            SI.customer = prj.customer
            SI.company = prj.company
            SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])

            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.taxes_and_charges=prj.sales_taxes_charges_template
            SI.tc_name=prj.terms
            if prj.price_list:
                SI.selling_price_list=prj.price_list
            if not prj.price_list and prj.customer:
                doc=frappe.get_doc("Customer",prj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center
            if prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.custom_advance_billed_until)+"\n To Date:"+str(advance_bill_until)+"\n (YYYY-MM-DD)",
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.custom_advance_billed_until)+"\n To Date:"+str(advance_bill_until)+"\n (YYYY-MM-DD)",
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if prj.terms:
                term=frappe.get_doc("Terms and Conditions",prj.terms)
                SI.terms=term.terms
            # SI.validate()
            SI.insert(ignore_permissions=True)
            if prj.auto_creation_doctype=="Sales Order":
                prj.start_date=SI.transaction_date
            if prj.auto_creation_doctype=="Sales Invoice":
                prj.start_date=SI.posting_date
            prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                                {'date': advance_bill_until, 'name': prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s   where name = %(name)s""",
                                {'date': advance_bill_until,'name': prj.name})
                frappe.db.commit()
            if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                SI.submit()

        advance_bill_until=getdate(frappe.utils.nowdate())
        advance_bill_until_start=getdate(prj.start_date)
        if  getdate(frappe.utils.nowdate())>getdate(prj.start_date):
            if prj.billing_frequency=="Weekly":
                advance_bill_until=advance_bill_until_start+timedelta(days=7)
            if prj.billing_frequency == "Monthly":
                advance_bill_until=advance_bill_until_start+timedelta(days=30)
            if prj.billing_frequency == "Quaterly":
                advance_bill_until=advance_bill_until_start+timedelta(days=90)
            if prj.billing_frequency == "Bi-Yearly":
                advance_bill_until=advance_bill_until_start+timedelta(days=180)
            if prj.billing_frequency == "Yearly":
                advance_bill_until=advance_bill_until_start+timedelta(days=360)
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = prj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = prj.sales_invoice_naming_series
            SI.customer = prj.customer
            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.company = prj.company
            SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])


            SI.taxes_and_charges=prj.sales_taxes_charges_template
            SI.tc_name=prj.terms
            if prj.price_list:
                SI.selling_price_list=prj.price_list
            if not prj.price_list and prj.customer:
                doc=frappe.get_doc("Customer",prj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center,
            if prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n [YYYY-MM-DD]"+str(advance_bill_until_start)+"\n To Date:"+str(advance_bill_until)+"\n [YYYY-MM-DD]",
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n [YYYY-MM-DD]"+str(advance_bill_until_start)+"\n To Date:"+str(advance_bill_until)+"\n[YYYY-MM-DD]",
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if prj.terms:
                term=frappe.get_doc("Terms and Conditions",prj.terms)
                SI.terms=term.terms
            # SI.validate()
            SI.insert(ignore_permissions=True)
        
            if prj.auto_creation_doctype=="Sales Order":
                prj.start_date=SI.transaction_date
            if prj.auto_creation_doctype=="Sales Invoice":
                prj.start_date=SI.posting_date
            prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s  where name = %(name)s""",
                                {'date': advance_bill_until, 'name': prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s  where name = %(name)s""",
                                {'date': advance_bill_until,'name': prj.name})
                frappe.db.commit()
            if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                SI.submit()


        if prj.billing_frequency == "Custom":
            delta = frappe.utils.nowdate()
            lst = delta.split("-")
            exact_date = lst[2]
           
            specified_dates = frappe.db.sql(""" select day_number from `tabTimesheet Days` where parent=%(name)s """,{'name':prj.name},as_dict=1)
            for days in specified_dates:
                if days['day_number'] == int(exact_date) and getdate(frappe.utils.nowdate())>getdate(prj.start_date):
                    advance_bill_until= prj.start_date+timedelta(days=days['day_number'])
                    # advance_bill_until=advance_bill_until_start+datetime.timedelta(days=days['day_number'])
                    doctype = prj.auto_creation_doctype
                    SI = frappe.new_doc(doctype)
                    if doctype == "Sales Order":
                        SI.naming_series = prj.sales_order_naming_series
                        SI.delivery_date = frappe.utils.nowdate()
                    if doctype == "Sales Invoice":
                        SI.naming_series = prj.sales_invoice_naming_series
                    SI.customer = prj.customer
                    SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])

                    SI.currency = prj.currency
                    SI.due_date = frappe.utils.nowdate()
                    SI.project = prj.name
                    SI.company = prj.company

                    SI.taxes_and_charges=prj.sales_taxes_charges_template
                    SI.tc_name=prj.terms
                    if prj.price_list:
                        SI.selling_price_list=prj.price_list
                    if not prj.price_list and prj.customer:
                        doc=frappe.get_doc("Customer",prj.customer)
                        if doc.default_price_list:
                            SI.selling_price_list=doc.default_price_list
                    company=frappe.get_doc("Company",prj.company)
                    SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center
                    if prj.auto_creation_doctype=="Sales Invoice":
                        SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(advance_bill_until_start)+"\n To Date:"+str(advance_bill_until)+"\n (YYYY-MM-DD)",
                        SI.append("items", {
                            "item_code": prj.recurring_item,
                            "qty": 1,
                            "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                            "uom":prj.custom_uom,
                            "project":prj.name,
                            "rate": prj.recurring_charges,
                            "conversion_factor": 1,
                        })
                    if prj.auto_creation_doctype=="Sales Order":
                        SI.append("items", {
                            "item_code": prj.recurring_item,
                            "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(advance_bill_until_start)+"\n To Date:"+str(advance_bill_until)+"\n (YYYY-MM-DD)",
                            "qty": 1,
                            "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                            "uom":prj.custom_uom,
                            "project":prj.name,
                            "rate": prj.recurring_charges,
                            "conversion_factor": 1,
                        })
                    if prj.sales_taxes_charges_template:
                        tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                        for i in tax.taxes:
                            SI.append("taxes", {
                                "charge_type": i.charge_type,
                                "description":i.description,
                                "account_head": i.account_head,
                                "rate": i.rate
                            })
                    if prj.terms:
                        term=frappe.get_doc("Terms and Conditions",prj.terms)
                        SI.terms=term.terms
                    # SI.validate()
                    SI.insert(ignore_permissions=True)
                    
                    if prj.auto_creation_doctype=="Sales Order":
                        prj.start_date=SI.transaction_date
                    if prj.auto_creation_doctype=="Sales Invoice":
                        prj.start_date=SI.posting_date
                    prj.save(ignore_permissions=True)
                    if doctype == "Sales Order":
                        frappe.db.sql(""" update `tabProject` set start_date = %(date)s  where name = %(name)s""",
                                      {'date': advance_bill_until, 'name': prj.name})
                        frappe.db.commit()
                    if doctype == "Sales Invoice":
                        frappe.db.sql(""" update `tabProject` set start_date = %(date)s   where name = %(name)s""",
                                      {'date': advance_bill_until,'name': prj.name})
                        frappe.db.commit()
                    if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                        SI.submit()

                    break
#     new timesheet
    time_project = frappe.db.sql(""" select name from `tabProject`
                                            where billing_based_on = 'Timesheet Based' and status = "Open" and is_active="Yes"
                                            """, as_dict=True)
    lst = []
    for proj in time_project:
        tprj = frappe.get_doc("Project", proj['name'])
        delta = getdate(frappe.utils.nowdate()) - tprj.start_date
        if tprj.billing_frequency == "Weekly" and int(delta.days) >= 7 or tprj.billing_frequency == "Monthly" and int(
                delta.days) >= 30 or tprj.billing_frequency == "Quaterly" and int(
                delta.days) >= 90 or tprj.billing_frequency == "Bi-Yearly" and int(
            delta.days) >= 180 or tprj.billing_frequency == "Yearly" and int(delta.days) >= 360 or tprj.billing_frequency == "Daily":
            doctype = tprj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = tprj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = tprj.sales_invoice_naming_series
            SI.customer = tprj.customer
            SI.currency = tprj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = tprj.name
            SI.company = tprj.company
            SI.taxes_and_charges=tprj.sales_taxes_charges_template
            SI.letter_head=frappe.db.get_value("Company",{"name":tprj.company},["default_letter_head"])

            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=tprj.cost_center if tprj.cost_center else company.cost_center
            if tprj.terms:
                SI.tc_name=tprj.terms
            if tprj.price_list:
                SI.selling_price_list=tprj.price_list
            if not tprj.price_list and tprj.customer:
                doc=frappe.get_doc("Customer",tprj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            abs_val = 0
            timesheet = frappe.db.sql(""" select distinct parent from `tabTimesheet Detail` where project = "{0}" 
                                      and (COALESCE(sales_invoice,'')='' AND COALESCE(sales_order,'')='') and docstatus=1 
                                      and  is_billable=1
                                    and billing_amount>0 and from_time >= '{1}'""".format(proj['name'],tprj.start_date),as_dict=1)
            qty=[]
            bil=[]
            for tsheet in timesheet:
                ttsheet_obj = frappe.get_doc("Timesheet", tsheet.get("parent"))
               
                if ttsheet_obj.per_billed < 100 and ttsheet_obj.total_billable_hours and ttsheet_obj.total_billable_hours > ttsheet_obj.total_billed_hours and ttsheet_obj.docstatus == 1:
                    tsheet_obj = frappe.get_doc("Timesheet", ttsheet_obj.name)
                    if flt(tsheet_obj.total_billable_hours) > 0:

                        hours = flt(tsheet_obj.total_billable_hours) - flt(tsheet_obj.total_billed_hours)
                        billing_amount = flt(tsheet_obj.total_billable_amount) - flt(tsheet_obj.total_billed_amount)
                        billing_rate = 1
                        if hours > 0:
                            billing_rate = billing_amount / hours

                        
                        if tsheet_obj.per_billed < 100 and tsheet_obj.total_billable_hours and tsheet_obj.total_billable_hours > tsheet_obj.total_billed_hours and tsheet_obj.docstatus == 1:
                            abs_val = 1
                            for i in tsheet_obj.time_logs:
                                if i.project==tprj.name and i.is_billable==1:
                                    if doctype == "Sales Invoice":
                                        SI.append("timesheets", {
                                            "activity_type":i.activity_type,
                                            "description":i.description,
                                            "from_time":i.from_time,
                                            "to_time":i.to_time,
                                            "project_name":i.project_name,
                                            "time_sheet": tsheet_obj.name,
                                            "billing_hours": i.billing_hours,
                                            "billing_amount": i.billing_rate*i.billing_hours,
                                            "from__date":i.from_date
                                            })
                                    lst.append(tsheet_obj.name)
                                    qty.append(i.billing_hours)
                                    bil.append(i.billing_rate*i.billing_hours)

            q=sum(qty)
            s=sum(bil)
            if s > 0 and q >0:
                if tprj.auto_creation_doctype=="Sales Order":
                    SI.append("items", {
                        "item_code": tprj.timesheet_item,
                        "description":"Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                        "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                        "uom":tprj.custom_uom,
                        "project":tprj.name,
                        "qty": q,
                        "rate": s/q,
                        "conversion_factor": 1,
                    })
                if tprj.auto_creation_doctype=="Sales Invoice":
                    SI.remarks="Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                    SI.append("items", {
                        "item_code": tprj.timesheet_item,
                        "qty": q,
                        "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                        "uom":tprj.custom_uom,
                        "project":tprj.name,
                        "rate": s/q,
                        "conversion_factor": 1,
                    })
                if tprj.sales_taxes_charges_template:
                    tax=frappe.get_doc("Sales Taxes and Charges Template",tprj.sales_taxes_charges_template)
                    for i in tax.taxes:
                        SI.append("taxes", {
                            "charge_type": i.charge_type,
                            "description":i.description,
                            "account_head": i.account_head,
                            "rate": i.rate
                        })
                if tprj.terms:
                    term=frappe.get_doc("Terms and Conditions",tprj.terms)
                    SI.terms=term.terms
                if abs_val==1:
                    SI.save(ignore_permissions=True)
                    SI.validate()
                    if tprj.auto_creation_doctype=="Sales Order":
                        tprj.start_date=SI.transaction_date
                    if tprj.auto_creation_doctype=="Sales Invoice":
                        tprj.start_date=SI.posting_date
                    tprj.save(ignore_permissions=True)
                    tprj.reload()
                    SI.flags.ignore_validate_update_after_submit = True
                    if tprj.auto_submit_invoice == 1 or tprj.auto_submit_order == 1:
                        SI.validate()
                        SI.submit()
                        for time_sheet in set(lst):
                            timesheet_obj = frappe.get_doc("Timesheet", time_sheet)
                            amount=[]
                            for i in timesheet_obj.time_logs:
                                if i.project==tprj.name:
                                    amount.append(i.billing_amount)
                            hours = flt(timesheet_obj.total_billable_hours) - flt(timesheet_obj.total_billed_hours)
                            billing_amount = flt(timesheet_obj.total_billable_amount) - flt(
                                timesheet_obj.total_billed_amount)
                            if hours > 0:
                                billing_rate = billing_amount / hours
                            if timesheet_obj.total_billable_amount:
                                timesheet_obj.per_billed = (sum(amount) * 100) / timesheet_obj.total_billable_amount
                            # if timesheet_obj.per_billed == 100:

                            #     frappe.db.sql(
                            #         """ update `tabTimesheet` set total_billed_amount = %(total_billed_amount)s, per_billed= %(per_billed)s,
                            #             status = "Billed",total_billed_hours = %(hours)s where name = %(name)s""",
                            #         {'total_billed_amount': billing_amount, 'name': timesheet_obj.name,
                            #             'per_billed': timesheet_obj.per_billed,
                            #             'hours': hours})
                            #     frappe.db.commit()
                            #     if tprj.auto_creation_doctype == "Sales Invoice":
                            #         frappe.db.sql(
                            #             """ update `tabTimesheet Detail` set sales_invoice = %(name)s where parent = %(parent)s  and project=%(project)s and is_billable=1""",
                            #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                            #         frappe.db.commit()
                            #     if tprj.auto_creation_doctype == "Sales Order":
                            #         frappe.db.sql(
                            #             """ update `tabTimesheet Detail` set sales_order = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                            #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                            #         frappe.db.commit()
                            # else:
                            #     frappe.db.sql(
                            #         """ update `tabTimesheet` set total_billed_amount = %(total_billed_amount)s, per_billed= %(per_billed)s,
                            #             total_billed_hours = %(hours)s where name = %(name)s""",
                            #         {'total_billed_amount': sum(amount), 'name': timesheet_obj.name,
                            #             'per_billed': timesheet_obj.per_billed,
                            #             'hours': hours})
                            #     frappe.db.commit()

                            #     if tprj.auto_creation_doctype == "Sales Invoice":
                            #         frappe.db.sql(
                            #             """ update `tabTimesheet Detail` set sales_invoice = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                            #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                            #         frappe.db.commit()
                            #     if tprj.auto_creation_doctype == "Sales Order":
                            #         frappe.db.sql(
                            #             """ update `tabTimesheet Detail` set sales_order = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                            #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                            #         frappe.db.commit()

    time_project = frappe.db.sql(""" select name from `tabProject`
                                            where billing_based_on = 'Timesheet Based' and status = "Open" and is_active="Yes"
                                            """, as_dict=True)
    lst=[]
    for proj in time_project:
        tprj = frappe.get_doc("Project", proj['name'])
        if tprj.billing_frequency == "Custom":
            delta = frappe.utils.nowdate()
            lsta = delta.split("-")
            exact_date = lsta[2]
            specified_dates = frappe.db.sql(""" select day_number from `tabTimesheet Days` where parent='{0}'""".format(tprj.name),as_dict=1)
            for days in specified_dates:
                if days['day_number'] == int(exact_date):
                    doctype = tprj.auto_creation_doctype
                    SI = frappe.new_doc(doctype)
                    if doctype == "Sales Order":
                        SI.naming_series = tprj.sales_order_naming_series
                        SI.delivery_date = frappe.utils.nowdate()
                    if doctype == "Sales Invoice":
                        SI.naming_series = tprj.sales_invoice_naming_series
                    SI.customer = tprj.customer
                    SI.company=tprj.company
                    SI.currency = tprj.currency
                    SI.due_date = frappe.utils.nowdate()
                    SI.letter_head=frappe.db.get_value("Company",{"name":tprj.company},["default_letter_head"])

                    SI.project = tprj.name
                    SI.taxes_and_charges=tprj.sales_taxes_charges_template
                    if tprj.terms:
                        SI.tc_name=tprj.terms
                    if tprj.price_list:
                        SI.selling_price_list=tprj.price_list
                    if not tprj.price_list and tprj.customer:
                        doc=frappe.get_doc("Customer",tprj.customer)
                        if doc.default_price_list:
                            SI.selling_price_list=doc.default_price_list
                    abs_val = 0
                    company=frappe.get_doc("Company",tprj.company)
                    SI.cost_center=tprj.cost_center if tprj.cost_center else company.cost_center,
                    timesheet = frappe.db.sql(""" select distinct parent from `tabTimesheet Detail` where project = "{0}" and (COALESCE(sales_invoice,'')='' AND COALESCE(sales_order,'')='')
                                              and docstatus=1 and  is_billable=1
                                            and billing_amount>0 and from_time >= '{1}'""".format(proj['name'],tprj.start_date),as_dict=1)

                    qty=[]
                    bil=[]
                    for tsheet in timesheet:
                        ttsheet_obj = frappe.get_doc("Timesheet", tsheet.get("parent"))

                    
                        if ttsheet_obj.per_billed < 100 and ttsheet_obj.docstatus == 1:
                            tsheet_obj = frappe.get_doc("Timesheet", ttsheet_obj.name)
                            abs_val = 1
                            for i in tsheet_obj.time_logs:
                                if i.project==tprj.name and i.is_billable==1:
                                    if doctype == "Sales Invoice":
                                        SI.append("timesheets", {
                                            "activity_type":i.activity_type,
                                            "description":i.description,
                                            "from_time":i.from_time,
                                            "to_time":i.to_time,
                                            "project_name":i.project_name,
                                            "time_sheet": tsheet_obj.name,
                                            "billing_hours": i.billing_hours,
                                            "billing_amount": i.billing_rate*i.billing_hours,
                                            "from__date":i.from_date
                                            })
                                    lst.append(tsheet_obj.name)
                                    qty.append(i.billing_hours)
                                    bil.append(i.billing_rate*i.billing_hours)

                    q=sum(qty)
                    s=sum(bil)
                    if s > 0 and q >0:
                        if tprj.auto_creation_doctype=="Sales Order":
                            SI.append("items", {
                            "item_code": tprj.timesheet_item,
                            "description":"Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                            "qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>q else q,
                            "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                            "uom":tprj.custom_uom,
                            "project":tprj.name,
                            "rate": s/q,
                            "conversion_factor": 1,
                        })
                        if tprj.auto_creation_doctype=="Sales Invoice":
                            SI.remarks="Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                            SI.append("items", {
                                "item_code": tprj.timesheet_item,
                                "qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>q else q,
                                "rate": s/q,
                                "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                                "uom":tprj.custom_uom,
                                "project":tprj.name,
                                "conversion_factor": 1,
                            })
                        if tprj.sales_taxes_charges_template:
                            tax=frappe.get_doc("Sales Taxes and Charges Template",tprj.sales_taxes_charges_template)
                            for i in tax.taxes:
                                SI.append("taxes", {
                                    "charge_type": i.charge_type,
                                    "description":i.description,
                                    "account_head": i.account_head,
                                    "rate": i.rate
                                })
                        if tprj.terms:
                            term=frappe.get_doc("Terms and Conditions",tprj.terms)
                            SI.terms=term.terms
                        if abs_val==1:
                            SI.save(ignore_permissions=True)
                            SI.validate()
                            if tprj.auto_creation_doctype=="Sales Order":
                                tprj.start_date=SI.transaction_date
                            if tprj.auto_creation_doctype=="Sales Invoice":
                                tprj.start_date=SI.posting_date
                            tprj.save(ignore_permissions=True)
                            tprj.reload()
                            SI.flags.ignore_validate_update_after_submit = True
                            if tprj.auto_submit_invoice == 1 or tprj.auto_submit_order == 1:
                                SI.validate()
                                SI.submit()
                                for time_sheet in set(lst):
                                    timesheet_obj = frappe.get_doc("Timesheet", time_sheet)
                                    amount=[]
                                    for i in timesheet_obj.time_logs:
                                        if i.project==tprj.name:
                                            amount.append(i.billing_amount)
                                    hours = flt(timesheet_obj.total_billable_hours) - flt(timesheet_obj.total_billed_hours)
                                    billing_amount = flt(timesheet_obj.total_billable_amount) - flt(
                                        timesheet_obj.total_billed_amount)
                                    if hours > 0:
                                        billing_rate = billing_amount / hours
                                    if timesheet_obj.total_billable_amount:
                                        timesheet_obj.per_billed = (sum(amount) * 100) / timesheet_obj.total_billable_amount
                                    # if timesheet_obj.per_billed == 100:

                                    #     frappe.db.sql(
                                    #         """ update `tabTimesheet` set total_billed_amount = %(total_billed_amount)s, per_billed= %(per_billed)s,
                                    #             status = "Billed",total_billed_hours = %(hours)s where name = %(name)s""",
                                    #         {'total_billed_amount': billing_amount, 'name': timesheet_obj.name,
                                    #             'per_billed': timesheet_obj.per_billed,
                                    #             'hours': hours})
                                    #     frappe.db.commit()
                                    #     if tprj.auto_creation_doctype == "Sales Invoice":
                                    #         frappe.db.sql(
                                    #             """ update `tabTimesheet Detail` set sales_invoice = %(name)s where parent = %(parent)s  and project=%(project)s and is_billable=1""",
                                    #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                                    #         frappe.db.commit()
                                    #     if tprj.auto_creation_doctype == "Sales Order":
                                    #         frappe.db.sql(
                                    #             """ update `tabTimesheet Detail` set sales_order = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                                    #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                                    #         frappe.db.commit()
                                    # else:
                                    #     frappe.db.sql(
                                    #         """ update `tabTimesheet` set total_billed_amount = %(total_billed_amount)s, per_billed= %(per_billed)s,
                                    #             total_billed_hours = %(hours)s where name = %(name)s""",
                                    #         {'total_billed_amount': sum(amount), 'name': timesheet_obj.name,
                                    #             'per_billed': timesheet_obj.per_billed,
                                    #             'hours': hours})
                                    #     frappe.db.commit()

                                    #     if tprj.auto_creation_doctype == "Sales Invoice":
                                    #         frappe.db.sql(
                                    #             """ update `tabTimesheet Detail` set sales_invoice = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                                    #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                                    #         frappe.db.commit()
                                    #     if tprj.auto_creation_doctype == "Sales Order":
                                    #         frappe.db.sql(
                                    #             """ update `tabTimesheet Detail` set sales_order = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                                    #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                                    #         frappe.db.commit()


    
@frappe.whitelist()
def daily_method():
    time_project = frappe.db.sql(""" select name from `tabProject`
                                            where status = "Open" and billing_based_on != 'Free Of Charge' and is_active="Yes"
                                            """, as_dict=True)
    for proj in time_project:
        # issue=frappe.db.sql("""select name from `tabIssue` where dexciss_status="Closed" 
        #                    and (COALESCE(sales_invoice,'')='' AND COALESCE(sales_order,'')='') and dexciss_status='Closed' and project='{0}'""".format(proj['name']),as_dict=1)
        task=frappe.db.sql("""select name from `tabTask` where status="Completed" and fixed_cost_based_billing=1
                           and (COALESCE(sales_invoice,'')='' AND COALESCE(sales_order,'')='')  and project='{0}'""".format(proj['name']),as_dict=1)
        tprj = frappe.get_doc("Project", proj['name'])
        if tprj.cr_last_billing_date:
            s=""
            for i in task:
                task=frappe.get_doc("Task",i.name)
                if task.expected_time>0 and task.completed_on:
                    doctype = tprj.auto_creation_doctype
                    SI = frappe.new_doc(doctype)
                    if doctype == "Sales Order":
                        SI.naming_series = tprj.sales_order_naming_series
                        SI.delivery_date = frappe.utils.nowdate()
                    if doctype == "Sales Invoice":
                        SI.naming_series = tprj.sales_invoice_naming_series
                    SI.customer = tprj.customer
                    SI.letter_head=frappe.db.get_value("Company",{"name":tprj.company},["default_letter_head"])

                    SI.currency = tprj.currency
                    SI.due_date = frappe.utils.nowdate()
                    SI.project = tprj.name
                    SI.company = tprj.company
                    SI.taxes_and_charges=tprj.sales_taxes_charges_template
                    if tprj.terms:
                        SI.tc_name=tprj.terms
                    if tprj.price_list:
                        selling_price_list=tprj.price_list
                    if not tprj.price_list and tprj.customer:
                        doc=frappe.get_doc("Customer",tprj.customer)
                        if doc.default_price_list:
                            selling_price_list=doc.default_price_list
                    SI.selling_price_list=selling_price_list
                    company=frappe.get_doc("Company",tprj.company)
                    SI.cost_center=tprj.cost_center if tprj.cost_center else company.cost_center
                    docval=frappe.db.get_value("Item Price",{"price_list":SI.selling_price_list,"item_code":tprj.cr_item},["price_list_rate"])
                    if task.expected_time:
                        if tprj.auto_creation_doctype == "Sales Invoice":
                            SI.remarks="Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type : CR INVOICE"+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                            SI.append("items", {
                                "item_code": tprj.cr_item,
                                "description":task.subject,
                                "qty": flt(task.expected_time),
                                "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                                "uom":tprj.custom_uom,
                                "project":tprj.name,
                                "rate":docval,
                                "conversion_factor": 1,
                            })
                        if tprj.auto_creation_doctype == "Sales Order":
                            SI.append("items", {
                                "item_code": tprj.cr_item,
                                "description":"Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type : CR INVOICE"+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                                "qty": flt(task.expected_time),
                                "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                                "uom":tprj.custom_uom,
                                "project":tprj.name,
                                "rate": docval,
                                "conversion_factor": 1,
                            })
                    if tprj.sales_taxes_charges_template:
                        tax=frappe.get_doc("Sales Taxes and Charges Template",tprj.sales_taxes_charges_template)
                        for i in tax.taxes:
                            SI.append("taxes", {
                                "charge_type": i.charge_type,
                                "description":i.description,
                                "account_head": i.account_head,
                                "rate": i.rate
                            })
                    if tprj.terms:
                        term=frappe.get_doc("Terms and Conditions",tprj.terms)
                        SI.terms=term.terms
                    
                    SI.save(ignore_permissions=True)
                    SI.flags.ignore_validate_update_after_submit = True
                    if tprj.auto_submit_invoice == 1 or tprj.auto_submit_order == 1:
                        SI.submit()         
                    if tprj.auto_creation_doctype == "Sales Invoice":
                        frappe.db.sql(
                            """ update `tabTask` set sales_invoice = %(name)s where name = %(parent)s  and project=%(project)s """,
                            {'parent': task.name, 'name': SI.name,"project":tprj.name})
                        frappe.db.commit()
                    if tprj.auto_creation_doctype == "Sales Order":
                        frappe.db.sql(
                            """ update `tabTask` set sales_order = %(name)s where name = %(parent)s and project=%(project)s """,
                            {'parent': task.name, 'name': SI.name,"project":tprj.name})
                        frappe.db.commit()
                        



@frappe.whitelist()
def daily_project(project):

  # for billing based on milestone
    project_mil = frappe.db.sql(""" select name from `tabProject`
                                where billing_based_on = 'Milestone Based' and status = "Open" and is_active="Yes" and name='{0}'
                                """.format(project),
                                as_dict= True)

    for proj in project_mil:
        Prj = frappe.get_doc("Project",proj['name'])
        doctype = Prj.auto_creation_doctype
        SI = frappe.new_doc(doctype)
        if doctype == "Sales Order":
            SI.naming_series = Prj.sales_order_naming_series
            SI.delivery_date = frappe.utils.nowdate()
        if doctype == "Sales Invoice":
            SI.naming_series = Prj.sales_invoice_naming_series
        SI.customer = Prj.customer
        SI.currency = Prj.currency
        SI.due_date = frappe.utils.nowdate()
        SI.project = Prj.name
        SI.company = Prj.company
        SI.letter_head=frappe.db.get_value("Company",{"name":Prj.company},["default_letter_head"])


        SI.taxes_and_charges=Prj.sales_taxes_charges_template
        SI.tc_name=Prj.terms
        if Prj.price_list:
            SI.selling_price_list=Prj.price_list
        if not Prj.price_list and Prj.customer:
            doc=frappe.get_doc("Customer",Prj.customer)
            if doc.default_price_list:
                SI.selling_price_list=doc.default_price_list
        project_list_task = frappe.db.sql(""" select milestone,billing_item,billing_percentage from `tabProject Milestone Child` 
                                            where progress = 100  and parent = %(proj)s 
                                             and (COALESCE(invoice,'')='' AND COALESCE(s_order,'')='')""",{'proj':proj['name']},as_dict=True)
        company=frappe.get_doc("Company",Prj.company)
        SI.cost_center=Prj.cost_center if Prj.cost_center else company.cost_center

        for task in project_list_task:
            if Prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(Prj.name)+"\n Project Name :"+str(Prj.project_name)+"\n Billing Type : Milestone Bill"+"\n Milestone Name :"+str(task["milestone"])
                SI.append("items", {
                    "item_code": task["billing_item"],
                    "qty": 1,
                    "cost_center":Prj.cost_center if Prj.cost_center else company.cost_center,
                    "uom":Prj.custom_uom,
                    "project":Prj.name,
                    "rate": ((Prj.total_project_value_excluding_taxes * task["billing_percentage"]) / 100),
                    "conversion_factor": 1,
                })
            if Prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": task["billing_item"],
                    "description":"Project Code :"+str(Prj.name)+"\n Project Name :"+str(Prj.project_name)+"\n Billing Type : Milestone Bill"+"\n Milestone Name :"+str(task["milestone"]),
                    "qty": 1,
                    "rate": ((Prj.total_project_value_excluding_taxes * task["billing_percentage"]) / 100),
                    "conversion_factor": 1,
                    "cost_center":Prj.cost_center if Prj.cost_center else company.cost_center,
                    "uom":Prj.custom_uom,
                    "project":Prj.name,
                })
            if Prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",Prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if Prj.terms:
                term=frappe.get_doc("Terms and Conditions",Prj.terms)
                SI.terms=term.terms
        if len(project_list_task) > 0:
            # SI.validate()
            SI.insert(ignore_permissions=True)
            SI.save(ignore_permissions=True)
            if Prj.auto_creation_doctype=="Sales Order":
                Prj.start_date=SI.transaction_date
            if Prj.auto_creation_doctype=="Sales Invoice":
                Prj.start_date=SI.posting_date
            Prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject Milestone Child` set s_order = %(name)s where parent = %(parent)s""",
                              {'name': SI.name, 'parent': Prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject Milestone Child` set invoice = %(name)s where parent = %(parent)s""",
                              {'name': SI.name, 'parent': Prj.name})
                frappe.db.commit()
            if Prj.auto_submit_invoice == 1 or Prj.auto_submit_order == 1:
                SI.submit()


   # for biiling based on fixed recurring

    recc_project = frappe.db.sql(""" select name from `tabProject`
                                    where billing_based_on = 'Fixed Recurring' and status = "Open" and is_active="Yes"
                                  and custom_to_be_billed_in_advance =0 and name='{0}'
                                    """.format(project),as_dict=True)
    for proj in recc_project:
        prj = frappe.get_doc("Project", proj['name'])
        if prj.billing_frequency == "Daily":
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = prj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = prj.sales_invoice_naming_series
            SI.customer = prj.customer
            SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])

            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.company = prj.company
            SI.taxes_and_charges=prj.sales_taxes_charges_template
            SI.tc_name=prj.terms
            if prj.price_list:
                SI.selling_price_list=prj.price_list
            if not prj.price_list and prj.customer:
                doc=frappe.get_doc("Customer",prj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list

            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center

            if prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                    "qty": 1,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                })
            if prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if prj.terms:
                term=frappe.get_doc("Terms and Conditions",prj.terms)
                SI.terms=term.terms
            # SI.validate()
            SI.insert(ignore_permissions=True)
            # SI.save(ignore_permissions=True)
            if prj.auto_creation_doctype=="Sales Order":
                prj.start_date=SI.transaction_date
            if prj.auto_creation_doctype=="Sales Invoice":
                prj.start_date=SI.posting_date
            prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                              {'date': frappe.utils.nowdate(), 'name': prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                              {'date': frappe.utils.nowdate(), 'name': prj.name})
                frappe.db.commit()
            if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                SI.submit()


        delta = getdate(frappe.utils.nowdate()) - getdate(prj.start_date)
        if prj.billing_frequency == "Weekly" and int(delta.days) >= 7 or prj.billing_frequency == "Monthly" and int(delta.days) >= 30 or prj.billing_frequency == "Quaterly" and int(
            delta.days) >= 90 or prj.billing_frequency == "Bi-Yearly" and int(delta.days) >= 180 or prj.billing_frequency == "Yearly" and int(delta.days) >= 360:
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = prj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = prj.sales_invoice_naming_series
            SI.customer = prj.customer
            SI.company = prj.company
            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])

            SI.taxes_and_charges=prj.sales_taxes_charges_template
            SI.tc_name=prj.terms
            if prj.price_list:
                SI.selling_price_list=prj.price_list
            if not prj.price_list and prj.customer:
                doc=frappe.get_doc("Customer",prj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center

            if prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                    "qty": 1,
                     "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if prj.terms:
                term=frappe.get_doc("Terms and Conditions",prj.terms)
                SI.terms=term.terms
            # SI.validate()
            SI.insert(ignore_permissions=True)
            if prj.auto_creation_doctype=="Sales Order":
                prj.start_date=SI.transaction_date
            if prj.auto_creation_doctype=="Sales Invoice":
                prj.start_date=SI.posting_date
            prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                              {'date': frappe.utils.nowdate(), 'name': prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                              {'date': frappe.utils.nowdate(), 'name': prj.name})
                frappe.db.commit()
            if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                SI.submit()


        if prj.billing_frequency == "Custom":
            delta = frappe.utils.nowdate()
            lst = delta.split("-")
            exact_date = lst[2]
            specified_dates = frappe.db.sql(""" select day_number from `tabTimesheet Days` where parent=%(name)s """,{'name':prj.name},as_dict=1)
            for days in specified_dates:
                if days['day_number'] == int(exact_date):
                    doctype = prj.auto_creation_doctype
                    SI = frappe.new_doc(doctype)
                    if doctype == "Sales Order":
                        SI.naming_series = prj.sales_order_naming_series
                        SI.delivery_date = frappe.utils.nowdate()
                    if doctype == "Sales Invoice":
                        SI.naming_series = prj.sales_invoice_naming_series
                    SI.customer = prj.customer
                    SI.currency = prj.currency
                    SI.due_date = frappe.utils.nowdate()
                    SI.project = prj.name
                    SI.company = prj.company
                    SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])

                    SI.taxes_and_charges=prj.sales_taxes_charges_template
                    SI.tc_name=prj.terms
                    if prj.price_list:
                        SI.selling_price_list=prj.price_list
                    if not prj.price_list and prj.customer:
                        doc=frappe.get_doc("Customer",prj.customer)
                        if doc.default_price_list:
                            SI.selling_price_list=doc.default_price_list
                    company=frappe.get_doc("Company",prj.company)
                    SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center

                    if prj.auto_creation_doctype=="Sales Invoice":
                        SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                        SI.append("items", {
                            "item_code": prj.recurring_item,
                            "qty": 1,
                            "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                            "uom":prj.custom_uom,
                            "project":prj.name,                            
                            "rate": prj.recurring_charges,
                            "conversion_factor": 1,
                        })
                    if prj.auto_creation_doctype=="Sales Order":
                        SI.append("items", {
                            "item_code": prj.recurring_item,
                            "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.start_date)+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                            "qty": 1,
                            "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                            "uom":prj.custom_uom,
                            "project":prj.name,
                            "rate": prj.recurring_charges,
                            "conversion_factor": 1,
                        })
                    if prj.sales_taxes_charges_template:
                        tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                        for i in tax.taxes:
                            SI.append("taxes", {
                                "charge_type": i.charge_type,
                                "description":i.description,
                                "account_head": i.account_head,
                                "rate": i.rate
                            })
                    if prj.terms:
                        term=frappe.get_doc("Terms and Conditions",prj.terms)
                        SI.terms=term.terms
                    # SI.validate()
                    SI.insert(ignore_permissions=True)
                    if prj.auto_creation_doctype=="Sales Order":
                        prj.start_date=SI.transaction_date
                    if prj.auto_creation_doctype=="Sales Invoice":
                        prj.start_date=SI.posting_date
                    prj.save(ignore_permissions=True)
                    if doctype == "Sales Order":
                        frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                                      {'date': frappe.utils.nowdate(), 'name': prj.name})
                        frappe.db.commit()
                    if doctype == "Sales Invoice":
                        frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                                      {'date': frappe.utils.nowdate(), 'name': prj.name})
                        frappe.db.commit()
                    if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                        SI.submit()

                    break
  
    # for Advance biiling based on fixed recurring
    recc_project = frappe.db.sql(""" select name from `tabProject`
                                    where billing_based_on = 'Fixed Recurring' and status = "Open" and is_active="Yes" and custom_to_be_billed_in_advance=1 and name='{0}'
                                    """.format(project),as_dict=True)
    for proj in recc_project:
        prj = frappe.get_doc("Project", proj['name'])
        if prj.billing_frequency == "Daily" and getdate(frappe.utils.nowdate())>getdate(prj.start_date):
            advance_bill_until=getdate(prj.start_date)+timedelta(days=1)
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = prj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = prj.sales_invoice_naming_series
            SI.customer = prj.customer
            SI.company = prj.company
            SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])


            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.taxes_and_charges=prj.sales_taxes_charges_template
            SI.tc_name=prj.terms
            if prj.price_list:
                SI.selling_price_list=prj.price_list
            if not prj.price_list and prj.customer:
                doc=frappe.get_doc("Customer",prj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center

            if prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.custom_advance_billed_until)+"\n To Date:"+str(advance_bill_until)+"\n (YYYY-MM-DD)",
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "qty": 1,
                      "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(prj.custom_advance_billed_until)+"\n To Date:"+str(advance_bill_until)+"\n (YYYY-MM-DD)",
                    "qty": 1,
                      "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if prj.terms:
                term=frappe.get_doc("Terms and Conditions",prj.terms)
                SI.terms=term.terms
            # SI.validate()
            SI.insert(ignore_permissions=True)
            if prj.auto_creation_doctype=="Sales Order":
                prj.start_date=SI.transaction_date
            if prj.auto_creation_doctype=="Sales Invoice":
                prj.start_date=SI.posting_date
            prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s where name = %(name)s""",
                                {'date': advance_bill_until, 'name': prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s   where name = %(name)s""",
                                {'date': advance_bill_until,'name': prj.name})
                frappe.db.commit()
            if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                SI.submit()

        advance_bill_until=getdate(frappe.utils.nowdate())
        advance_bill_until_start=getdate(prj.start_date)
        if  getdate(frappe.utils.nowdate())>getdate(prj.start_date):
            if prj.billing_frequency=="Weekly":
                advance_bill_until=advance_bill_until_start+timedelta(days=7)
            if prj.billing_frequency == "Monthly":
                advance_bill_until=advance_bill_until_start+timedelta(days=30)
            if prj.billing_frequency == "Quaterly":
                advance_bill_until=advance_bill_until_start+timedelta(days=90)
            if prj.billing_frequency == "Bi-Yearly":
                advance_bill_until=advance_bill_until_start+timedelta(days=180)
            if prj.billing_frequency == "Yearly":
                advance_bill_until=advance_bill_until_start+timedelta(days=360)
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = prj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = prj.sales_invoice_naming_series
            SI.customer = prj.customer
            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])

            SI.project = prj.name
            SI.company = prj.company

            SI.taxes_and_charges=prj.sales_taxes_charges_template
            SI.tc_name=prj.terms
            if prj.price_list:
                SI.selling_price_list=prj.price_list
            if not prj.price_list and prj.customer:
                doc=frappe.get_doc("Customer",prj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            company=frappe.get_doc("Company",prj.company)
            SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center

            if prj.auto_creation_doctype=="Sales Invoice":
                SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n [YYYY-MM-DD]"+str(advance_bill_until_start)+"\n To Date:"+str(advance_bill_until)+"\n [YYYY-MM-DD]",
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.auto_creation_doctype=="Sales Order":
                SI.append("items", {
                    "item_code": prj.recurring_item,
                    "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n [YYYY-MM-DD]"+str(advance_bill_until_start)+"\n To Date:"+str(advance_bill_until)+"\n[YYYY-MM-DD]",
                    "qty": 1,
                    "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                    "uom":prj.custom_uom,
                    "project":prj.name,
                    "rate": prj.recurring_charges,
                    "conversion_factor": 1,
                })
            if prj.sales_taxes_charges_template:
                tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                for i in tax.taxes:
                    SI.append("taxes", {
                        "charge_type": i.charge_type,
                        "description":i.description,
                        "account_head": i.account_head,
                        "rate": i.rate
                    })
            if prj.terms:
                term=frappe.get_doc("Terms and Conditions",prj.terms)
                SI.terms=term.terms
            # SI.validate()
            SI.insert(ignore_permissions=True)
        
            if prj.auto_creation_doctype=="Sales Order":
                prj.start_date=SI.transaction_date
            if prj.auto_creation_doctype=="Sales Invoice":
                prj.start_date=SI.posting_date
            prj.save(ignore_permissions=True)
            if doctype == "Sales Order":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s  where name = %(name)s""",
                                {'date': advance_bill_until, 'name': prj.name})
                frappe.db.commit()
            if doctype == "Sales Invoice":
                frappe.db.sql(""" update `tabProject` set start_date = %(date)s  where name = %(name)s""",
                                {'date': advance_bill_until,'name': prj.name})
                frappe.db.commit()
            if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                SI.submit()


        if prj.billing_frequency == "Custom":
            delta = frappe.utils.nowdate()
            lst = delta.split("-")
            exact_date = lst[2]
           
            specified_dates = frappe.db.sql(""" select day_number from `tabTimesheet Days` where parent=%(name)s """,{'name':prj.name},as_dict=1)
            for days in specified_dates:
                if days['day_number'] == int(exact_date) and getdate(frappe.utils.nowdate())>getdate(prj.start_date):
                    advance_bill_until= prj.start_date+timedelta(days=days['day_number'])
                    # advance_bill_until=advance_bill_until_start+datetime.timedelta(days=days['day_number'])
                    doctype = prj.auto_creation_doctype
                    SI = frappe.new_doc(doctype)
                    if doctype == "Sales Order":
                        SI.naming_series = prj.sales_order_naming_series
                        SI.delivery_date = frappe.utils.nowdate()
                    if doctype == "Sales Invoice":
                        SI.naming_series = prj.sales_invoice_naming_series
                    SI.customer = prj.customer
                    SI.currency = prj.currency
                    SI.letter_head=frappe.db.get_value("Company",{"name":prj.company},["default_letter_head"])

                    SI.due_date = frappe.utils.nowdate()
                    SI.project = prj.name
                    SI.company = prj.company

                    SI.taxes_and_charges=prj.sales_taxes_charges_template
                    SI.tc_name=prj.terms
                    if prj.price_list:
                        SI.selling_price_list=prj.price_list
                    if not prj.price_list and prj.customer:
                        doc=frappe.get_doc("Customer",prj.customer)
                        if doc.default_price_list:
                            SI.selling_price_list=doc.default_price_list
                    company=frappe.get_doc("Company",prj.company)
                    SI.cost_center=prj.cost_center if prj.cost_center else company.cost_center

                    if prj.auto_creation_doctype=="Sales Invoice":
                        SI.remarks="Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(advance_bill_until_start)+"\n To Date:"+str(advance_bill_until)+"\n (YYYY-MM-DD)",
                        SI.append("items", {
                            "item_code": prj.recurring_item,
                            "qty": 1,
                           "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                            "uom":prj.custom_uom,
                            "project":prj.name,
                            "rate": prj.recurring_charges,
                            "conversion_factor": 1,
                        })
                    if prj.auto_creation_doctype=="Sales Order":
                        SI.append("items", {
                            "item_code": prj.recurring_item,
                            "description":"Project Code :"+str(prj.name)+"\n Project Name :"+str(prj.project_name)+"\n Billing Type :"+str(prj.billing_based_on)+"\n From Date:"+"\n (YYYY-MM-DD)"+str(advance_bill_until_start)+"\n To Date:"+str(advance_bill_until)+"\n (YYYY-MM-DD)",
                            "qty": 1,
                            "cost_center":prj.cost_center if prj.cost_center else company.cost_center,
                            "uom":prj.custom_uom,
                            "project":prj.name,
                            "rate": prj.recurring_charges,
                            "conversion_factor": 1,
                        })
                    if prj.sales_taxes_charges_template:
                        tax=frappe.get_doc("Sales Taxes and Charges Template",prj.sales_taxes_charges_template)
                        for i in tax.taxes:
                            SI.append("taxes", {
                                "charge_type": i.charge_type,
                                "description":i.description,
                                "account_head": i.account_head,
                                "rate": i.rate
                            })
                    if prj.terms:
                        term=frappe.get_doc("Terms and Conditions",prj.terms)
                        SI.terms=term.terms
                    # SI.validate()
                    SI.insert(ignore_permissions=True)
                    
                    if prj.auto_creation_doctype=="Sales Order":
                        prj.start_date=SI.transaction_date
                    if prj.auto_creation_doctype=="Sales Invoice":
                        prj.start_date=SI.posting_date
                    prj.save(ignore_permissions=True)
                    if doctype == "Sales Order":
                        frappe.db.sql(""" update `tabProject` set start_date = %(date)s  where name = %(name)s""",
                                      {'date': advance_bill_until, 'name': prj.name})
                        frappe.db.commit()
                    if doctype == "Sales Invoice":
                        frappe.db.sql(""" update `tabProject` set start_date = %(date)s   where name = %(name)s""",
                                      {'date': advance_bill_until,'name': prj.name})
                        frappe.db.commit()
                    if prj.auto_submit_invoice == 1 or prj.auto_submit_order == 1:
                        SI.submit()

                    break

#     new timesheet
    time_project = frappe.db.sql(""" select name from `tabProject`
                                            where billing_based_on = 'Timesheet Based' and status = "Open" and is_active="Yes" and name='{0}'
                                            """.format(project), as_dict=True)
    lst = []
    for proj in time_project:
        tprj = frappe.get_doc("Project", proj['name'])
        delta = getdate(frappe.utils.nowdate()) - tprj.start_date
        if tprj.billing_frequency == "Weekly" and int(delta.days) >= 7 or tprj.billing_frequency == "Monthly" and int(
                delta.days) >= 30 or tprj.billing_frequency == "Quaterly" and int(
            delta.days) >= 90 or tprj.billing_frequency == "Bi-Yearly" and int(
            delta.days) >= 180 or tprj.billing_frequency == "Yearly" and int(delta.days) >= 360 or tprj.billing_frequency == "Daily":
            doctype = tprj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.naming_series = tprj.sales_order_naming_series
                SI.delivery_date = frappe.utils.nowdate()
            if doctype == "Sales Invoice":
                SI.naming_series = tprj.sales_invoice_naming_series
            SI.customer = tprj.customer
            SI.currency = tprj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.letter_head=frappe.db.get_value("Company",{"name":tprj.company},["default_letter_head"])

            SI.project = tprj.name
            SI.company = tprj.company
            SI.taxes_and_charges=tprj.sales_taxes_charges_template
            if tprj.terms:
                SI.tc_name=tprj.terms
            if tprj.price_list:
                SI.selling_price_list=tprj.price_list
            if not tprj.price_list and tprj.customer:
                doc=frappe.get_doc("Customer",tprj.customer)
                if doc.default_price_list:
                    SI.selling_price_list=doc.default_price_list
            abs_val = 0
            timesheet = frappe.db.sql(""" select distinct parent from `tabTimesheet Detail` where project = "{0}"  and (COALESCE(sales_invoice,'')='' AND COALESCE(sales_order,'')='') 
                                      and docstatus=1 and  is_billable=1
                                                                    and billing_amount>0 and from_time >= '{1}'""".format(proj['name'],tprj.start_date),as_dict=1)
            qty=[]
            bil=[]
            for tsheet in timesheet:
                ttsheet_obj = frappe.get_doc("Timesheet", tsheet.get("parent"))
               
                if ttsheet_obj.per_billed < 100 and ttsheet_obj.total_billable_hours and ttsheet_obj.total_billable_hours > ttsheet_obj.total_billed_hours and ttsheet_obj.docstatus == 1:
                    tsheet_obj = frappe.get_doc("Timesheet", ttsheet_obj.name)
                    if flt(tsheet_obj.total_billable_hours) > 0:

                        hours = flt(tsheet_obj.total_billable_hours) - flt(tsheet_obj.total_billed_hours)
                        billing_amount = flt(tsheet_obj.total_billable_amount) - flt(tsheet_obj.total_billed_amount)
                        billing_rate = 1
                        if hours > 0:
                            billing_rate = billing_amount / hours

                        
                        if tsheet_obj.per_billed < 100 and tsheet_obj.total_billable_hours and tsheet_obj.total_billable_hours > tsheet_obj.total_billed_hours and tsheet_obj.docstatus == 1:
                            abs_val = 1
                            for i in tsheet_obj.time_logs:
                                if i.project==tprj.name and i.is_billable==1:
                                    if doctype == "Sales Invoice":
                                        SI.append("timesheets", {
                                            "activity_type":i.activity_type,
                                            "description":i.description,
                                            "from_time":i.from_time,
                                            "to_time":i.to_time,
                                            "project_name":i.project_name,
                                            "time_sheet": tsheet_obj.name,
                                            "billing_hours": i.billing_hours,
                                            "billing_amount": i.billing_rate*i.billing_hours,
                                            "from__date":i.from_date
                                            })
                                    lst.append(tsheet_obj.name)
                                    qty.append(i.billing_hours)
                                    bil.append(i.billing_rate*i.billing_hours)

            q=sum(qty)
            s=sum(bil)
            company=frappe.get_doc("Company",tprj.company)
            SI.cost_center=tprj.cost_center if tprj.cost_center else company.cost_center

            if s > 0 and q >0:
                if tprj.auto_creation_doctype=="Sales Order":
                    SI.append("items", {
                        "item_code": tprj.timesheet_item,
                        "description":"Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                        "qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>q else q,
                         "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                            "uom":tprj.custom_uom,
                            "project":tprj.name,
                        "rate": s/q,
                        "conversion_factor": 1,
                    })
                if tprj.auto_creation_doctype=="Sales Invoice":
                    SI.remarks="Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                    SI.append("items", {
                        "item_code": tprj.timesheet_item,
                        "qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>q else q,
                        "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                        "uom":tprj.custom_uom,
                        "project":tprj.name,
                        "rate": s/q,
                        "conversion_factor": 1,
                    })
                if tprj.sales_taxes_charges_template:
                    tax=frappe.get_doc("Sales Taxes and Charges Template",tprj.sales_taxes_charges_template)
                    for i in tax.taxes:
                        SI.append("taxes", {
                            "charge_type": i.charge_type,
                            "description":i.description,
                            "account_head": i.account_head,
                            "rate": i.rate
                        })
                if tprj.terms:
                    term=frappe.get_doc("Terms and Conditions",tprj.terms)
                    SI.terms=term.terms
                if abs_val==1:
                    SI.save(ignore_permissions=True)
                    SI.validate()
                    if tprj.auto_creation_doctype=="Sales Order":
                        tprj.start_date=SI.transaction_date
                    if tprj.auto_creation_doctype=="Sales Invoice":
                        tprj.start_date=SI.posting_date
                    tprj.save(ignore_permissions=True)
                    tprj.reload()
                    SI.flags.ignore_validate_update_after_submit = True
                    if tprj.auto_submit_invoice == 1 or tprj.auto_submit_order == 1:
                        SI.validate()
                        SI.submit()
                        for time_sheet in set(lst):
                            timesheet_obj = frappe.get_doc("Timesheet", time_sheet)
                            amount=[]
                            for i in timesheet_obj.time_logs:
                                if i.project==tprj.name:
                                    amount.append(i.billing_amount)
                            hours = flt(timesheet_obj.total_billable_hours) - flt(timesheet_obj.total_billed_hours)
                            billing_amount = flt(timesheet_obj.total_billable_amount) - flt(
                                timesheet_obj.total_billed_amount)
                            if hours > 0:
                                billing_rate = billing_amount / hours
                            if timesheet_obj.total_billable_amount:
                                timesheet_obj.per_billed = (sum(amount) * 100) / timesheet_obj.total_billable_amount
                            # if timesheet_obj.per_billed == 100:

                            #     frappe.db.sql(
                            #         """ update `tabTimesheet` set total_billed_amount = %(total_billed_amount)s, per_billed= %(per_billed)s,
                            #             status = "Billed",total_billed_hours = %(hours)s where name = %(name)s""",
                            #         {'total_billed_amount': billing_amount, 'name': timesheet_obj.name,
                            #             'per_billed': timesheet_obj.per_billed,
                            #             'hours': hours})
                            #     frappe.db.commit()
                            #     if tprj.auto_creation_doctype == "Sales Invoice":
                            #         frappe.db.sql(
                            #             """ update `tabTimesheet Detail` set sales_invoice = %(name)s where parent = %(parent)s  and project=%(project)s and is_billable=1""",
                            #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                            #         frappe.db.commit()
                            #     if tprj.auto_creation_doctype == "Sales Order":
                            #         frappe.db.sql(
                            #             """ update `tabTimesheet Detail` set sales_order = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                            #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                            #         frappe.db.commit()
                            # else:
                            #     frappe.db.sql(
                            #         """ update `tabTimesheet` set total_billed_amount = %(total_billed_amount)s, per_billed= %(per_billed)s,
                            #             total_billed_hours = %(hours)s where name = %(name)s""",
                            #         {'total_billed_amount': sum(amount), 'name': timesheet_obj.name,
                            #             'per_billed': timesheet_obj.per_billed,
                            #             'hours': hours})
                            #     frappe.db.commit()

                            #     if tprj.auto_creation_doctype == "Sales Invoice":
                            #         frappe.db.sql(
                            #             """ update `tabTimesheet Detail` set sales_invoice = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                            #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                            #         frappe.db.commit()
                            #     if tprj.auto_creation_doctype == "Sales Order":
                            #         frappe.db.sql(
                            #             """ update `tabTimesheet Detail` set sales_order = %(name)s where parent = %(parent)s and project=%(project)s and is_billable=1""",
                            #             {'parent': timesheet_obj.name, 'name': SI.name,"project":tprj.name})
                            #         frappe.db.commit()

   
    time_project = frappe.db.sql(""" select name from `tabProject`
                                            where billing_based_on = 'Timesheet Based' and status = "Open" and is_active="Yes" and name='{0}'
                                            """.format(project), as_dict=True)
    lst=[]
    for proj in time_project:
        tprj = frappe.get_doc("Project", proj['name'])
        if tprj.billing_frequency == "Custom":
            delta = frappe.utils.nowdate()
            lsta = delta.split("-")
            exact_date = lsta[2]
            specified_dates = frappe.db.sql(""" select day_number from `tabTimesheet Days` where parent='{0}'""".format(tprj.name),as_dict=1)
            for days in specified_dates:
                if days['day_number'] == int(exact_date):
                    doctype = tprj.auto_creation_doctype
                    SI = frappe.new_doc(doctype)
                    SI.company=tprj.company
                    if doctype == "Sales Order":
                        SI.naming_series = tprj.sales_order_naming_series
                        SI.delivery_date = frappe.utils.nowdate()
                    if doctype == "Sales Invoice":
                        SI.naming_series = tprj.sales_invoice_naming_series
                    SI.customer = tprj.customer
                    SI.currency = tprj.currency
                    SI.letter_head=frappe.db.get_value("Company",{"name":tprj.company},["default_letter_head"])

                    SI.due_date = frappe.utils.nowdate()
                    SI.project = tprj.name
                    SI.taxes_and_charges=tprj.sales_taxes_charges_template
                    if tprj.terms:
                        SI.tc_name=tprj.terms
                    if tprj.price_list:
                        SI.selling_price_list=tprj.price_list
                    if not tprj.price_list and tprj.customer:
                        doc=frappe.get_doc("Customer",tprj.customer)
                        if doc.default_price_list:
                            SI.selling_price_list=doc.default_price_list
                    abs_val = 0
                    company=frappe.get_doc("Company",tprj.company)
                    SI.cost_center=tprj.cost_center if tprj.cost_center else company.cost_center

                    timesheet = frappe.db.sql(""" select distinct parent from `tabTimesheet Detail` where project = "{0}" 
                                              and (COALESCE(sales_invoice,'')='' AND COALESCE(sales_order,'')='') 
                                              and docstatus=1 and  is_billable=1 
                                                                    and billing_amount>0 and from_time >= '{1}'""".format(proj['name'],tprj.start_date),as_dict=1)
                    qty=[]
                    bil=[]
                    for tsheet in timesheet:
                        ttsheet_obj = frappe.get_doc("Timesheet", tsheet.get("parent"))
                        if ttsheet_obj.per_billed < 100 and ttsheet_obj.docstatus == 1:
                            tsheet_obj = frappe.get_doc("Timesheet", ttsheet_obj.name)
                            abs_val = 1
                            for i in tsheet_obj.time_logs:
                                if i.project==tprj.name and i.is_billable==1:
                                    if doctype == "Sales Invoice":
                                        SI.append("timesheets", {
                                            "activity_type":i.activity_type,
                                            "description":i.description,
                                            "from_time":i.from_time,
                                            "to_time":i.to_time,
                                            "project_name":i.project_name,
                                            "time_sheet": tsheet_obj.name,
                                            "billing_hours": i.billing_hours,
                                            "billing_amount": i.billing_rate*i.billing_hours,
                                            "from__date":i.from_date
                                            })
                                    lst.append(tsheet_obj.name)
                                    qty.append(i.billing_hours)
                                    bil.append(i.billing_rate*i.billing_hours)

                    q=sum(qty)
                    s=sum(bil)
                    if s > 0 and q >0:
                        if tprj.auto_creation_doctype=="Sales Order":
                            SI.append("items", {
                            "item_code": tprj.timesheet_item,
                            "description":"Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                            "qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>q else q,
                            "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                            "uom":tprj.custom_uom,
                            "project":tprj.name,
                            "rate": s/q,
                            "conversion_factor": 1,
                        })
                        if tprj.auto_creation_doctype=="Sales Invoice":
                            SI.remarks="Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type :"+str(tprj.billing_based_on)+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                            SI.append("items", {
                                "item_code": tprj.timesheet_item,
                                "qty": tprj.custom_minimum_billing_hours if tprj.custom_minimum_billing_hours and  flt(tprj.custom_minimum_billing_hours)>q else q,
                                 "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                                "uom":tprj.custom_uom,
                                "project":tprj.name,
                                "rate": s/q,
                                "conversion_factor": 1,
                            })
                        if tprj.sales_taxes_charges_template:
                            tax=frappe.get_doc("Sales Taxes and Charges Template",tprj.sales_taxes_charges_template)
                            for i in tax.taxes:
                                SI.append("taxes", {
                                    "charge_type": i.charge_type,
                                    "description":i.description,
                                    "account_head": i.account_head,
                                    "rate": i.rate
                                })
                        if tprj.terms:
                            term=frappe.get_doc("Terms and Conditions",tprj.terms)
                            SI.terms=term.terms
                        if abs_val==1:
                            SI.save(ignore_permissions=True)
                            SI.validate()
                            if tprj.auto_creation_doctype=="Sales Order":
                                tprj.start_date=SI.transaction_date
                            if tprj.auto_creation_doctype=="Sales Invoice":
                                tprj.start_date=SI.posting_date
                            tprj.save(ignore_permissions=True)
                            tprj.reload()
                            SI.flags.ignore_validate_update_after_submit = True
                            if tprj.auto_submit_invoice == 1 or tprj.auto_submit_order == 1:
                                SI.validate()
                                SI.submit()
                                for time_sheet in set(lst):
                                    timesheet_obj = frappe.get_doc("Timesheet", time_sheet)
                                    amount=[]
                                    for i in timesheet_obj.time_logs:
                                        if i.project==tprj.name:
                                            amount.append(i.billing_amount)
                                    hours = flt(timesheet_obj.total_billable_hours) - flt(timesheet_obj.total_billed_hours)
                                    billing_amount = flt(timesheet_obj.total_billable_amount) - flt(
                                        timesheet_obj.total_billed_amount)
                                    if hours > 0:
                                        billing_rate = billing_amount / hours
                                    if timesheet_obj.total_billable_amount:
                                        timesheet_obj.per_billed = (sum(amount) * 100) / timesheet_obj.total_billable_amount
                



@frappe.whitelist()
def cr_method(project):

    time_project = frappe.db.sql(""" select name from `tabProject`
                                            where status = "Open" and is_active="Yes" and name='{0}'
                                            """.format(project), as_dict=True)
    selling_price_list=None
    for proj in time_project:
        task=frappe.db.sql("""select name from `tabTask` where status="Completed" and fixed_cost_based_billing=1
                           and (COALESCE(sales_invoice,'')='' AND COALESCE(sales_order,'')='')  and project='{0}'""".format(proj['name']),as_dict=1)
        tprj = frappe.get_doc("Project", proj['name'])
        if tprj.cr_last_billing_date:
            s=""
            for i in task:
                task=frappe.get_doc("Task",i.name)
                if task.expected_time>0 and task.completed_on:
                    doctype = tprj.auto_creation_doctype
                    SI = frappe.new_doc(doctype)
                    if doctype == "Sales Order":
                        SI.naming_series = tprj.sales_order_naming_series
                        SI.delivery_date = frappe.utils.nowdate()
                    if doctype == "Sales Invoice":
                        SI.naming_series = tprj.sales_invoice_naming_series
                    SI.customer = tprj.customer
                    SI.currency = tprj.currency
                    SI.due_date = frappe.utils.nowdate()
                    SI.project = tprj.name
                    SI.company = tprj.company
                    SI.taxes_and_charges=tprj.sales_taxes_charges_template
                    SI.letter_head=frappe.db.get_value("Company",{"name":tprj.company},["default_letter_head"])

                    if tprj.terms:
                        SI.tc_name=tprj.terms
                    if tprj.price_list:
                        selling_price_list=tprj.price_list
                    if not tprj.price_list and tprj.customer:
                        doc=frappe.get_doc("Customer",tprj.customer)
                        if doc.default_price_list:
                            selling_price_list=doc.default_price_list
                    SI.selling_price_list=selling_price_list
                    company=frappe.get_doc("Company",tprj.company)
                    SI.cost_center=tprj.cost_center if tprj.cost_center else company.cost_center

                    docval=frappe.db.get_value("Item Price",{"price_list":SI.selling_price_list,"item_code":tprj.cr_item},["price_list_rate"])
                    if task.expected_time:
                        if tprj.auto_creation_doctype == "Sales Invoice":
                            SI.remarks="Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type : CR INVOICE"+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                            SI.append("items", {
                                "item_code": tprj.cr_item,
                                "description":task.subject,
                                 "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                                "uom":tprj.custom_uom,
                                "project":tprj.name,
                                "qty": flt(task.expected_time),
                                "rate":docval,
                                "conversion_factor": 1,
                            })
                        if tprj.auto_creation_doctype == "Sales Order":
                            SI.append("items", {
                                "item_code": tprj.cr_item,
                                "description":"Project Code :"+str(tprj.name)+"\n Project Name :"+str(tprj.project_name)+"\n Billing Type : CR INVOICE"+"\n From Date:"+str(tprj.start_date)+"\n (YYYY-MM-DD)"+"\n To Date:"+str(frappe.utils.nowdate())+"\n (YYYY-MM-DD)",
                                "qty": flt(task.expected_time),
                                 "cost_center":tprj.cost_center if tprj.cost_center else company.cost_center,
                                "uom":tprj.custom_uom,
                                "project":tprj.name,
                                "rate": docval,
                                "conversion_factor": 1,
                            })
                    if tprj.sales_taxes_charges_template:
                        tax=frappe.get_doc("Sales Taxes and Charges Template",tprj.sales_taxes_charges_template)
                        for i in tax.taxes:
                            SI.append("taxes", {
                                "charge_type": i.charge_type,
                                "description":i.description,
                                "account_head": i.account_head,
                                "rate": i.rate
                            })
                    if tprj.terms:
                        term=frappe.get_doc("Terms and Conditions",tprj.terms)
                        SI.terms=term.terms
                    
                    SI.save(ignore_permissions=True)
                    SI.flags.ignore_validate_update_after_submit = True
                    if tprj.auto_submit_invoice == 1 or tprj.auto_submit_order == 1:
                        SI.submit()         
                    if tprj.auto_creation_doctype == "Sales Invoice":
                        frappe.db.sql(
                            """ update `tabTask` set sales_invoice = %(name)s where name = %(parent)s  and project=%(project)s """,
                            {'parent': task.name, 'name': SI.name,"project":tprj.name})
                        frappe.db.commit()
                    if tprj.auto_creation_doctype == "Sales Order":
                        frappe.db.sql(
                            """ update `tabTask` set sales_order = %(name)s where name = %(parent)s and project=%(project)s """,
                            {'parent': task.name, 'name': SI.name,"project":tprj.name})
                        frappe.db.commit()

def get_days_and_hours(self,method):
    if self.exp_start_date and self.exp_end_date and self.expected_time:
        sd = self.exp_start_date
        ed = self.exp_end_date
        now = getdate(sd)
        now1= getdate(ed)
        dlist = []

        Days =  (now1 -now).days + 1
        for i in range(Days):
            ob = frappe.utils.add_days(now, i)
            dlist.append(ob)

        res=[]
        if self.project:
            if self.primary_consultant:
                emp_holi = frappe.db.get_value("Employee",{"name":self.primary_consultant},["holiday_list"])
                hdlist = frappe.db.get_all("Holiday",{"parent":emp_holi},["holiday_date"])
                print("*********************",hdlist)
                if hdlist:
                    for dt in hdlist:
                        if dt.get("holiday_date") in dlist:
                            dlist.remove(dt.get("holiday_date"))
                            res = [i for i in dlist if i not in hdlist]

                else:
                    hlist = frappe.db.get_all("Holiday",{"parent":emp_holi},["holiday_date"])
                    for dt in hlist:
                        if dt.get("holiday_date") in dlist:
                            dlist.remove(dt.get("holiday_date"))
                            res = [i for i in dlist if i not in hlist]
            else:
                cmp = frappe.db.get_value("Project",{"name":self.project},["company"])
                if cmp:
                    comp = frappe.get_doc("Company",cmp)
                    hdlist = frappe.db.get_all("Holiday",{"parent":comp.default_holiday_list},["holiday_date"])
                    if hdlist:
                        for dt in hdlist:
                            if dt.get("holiday_date") in dlist:
                                dlist.remove(dt.get("holiday_date"))
                                res = [i for i in dlist if i not in hdlist]

                    else:
                        hlist = frappe.db.get_all("Holiday",{"parent":comp.default_holiday_list},["holiday_date"])
                        for dt in hlist:
                            if dt.get("holiday_date") in dlist:
                                dlist.remove(dt.get("holiday_date"))
                                res = [i for i in dlist if i not in hlist]
                            

                else:
                    comp = frappe.get_doc("Company",frappe.defaults.get_user_default("company"))
                    hdlist = frappe.db.get_all("Holiday",{"parent":comp.default_holiday_list},["holiday_date"])
                    if hdlist:
                        for dt in hdlist:
                            if dt.get("holiday_date") in dlist:
                                dlist.remove(dt.get("holiday_date"))
                                res = [i for i in dlist if i not in hdlist]

                    else:
                        hlist = frappe.db.get_all("Holiday",{"parent":comp.default_holiday_list},["holiday_date"])
                        for dt in hlist:
                            if dt.get("holiday_date") in dlist:
                                dlist.remove(dt.get("holiday_date"))
                                res = [i for i in dlist if i not in hlist]





        self.total_duration_in_days = len(res) if len(res) > 0 else Days

        dh = float(self.expected_time)/len(res) if len(res) > 0 else float(self.expected_time)/Days
        self.duration_per_day_in_hours = dh

    


@frappe.whitelist()
def allocation_based_billing():
        
    #Billing For Allocation-Based Projects


    time_project = frappe.db.sql(""" select name from `tabProject`
                                    where billing_based_on = 'Allocation Based' and status = "Open" and is_active="Yes"
                                        """, as_dict=True)
    
    for proj in time_project:
        tprj = frappe.get_doc("Project", proj['name'])
            

        last_billed_date = getdate(tprj.last_billing_date).strftime("%Y-%m-%d")
        today = getdate(frappe.utils.nowdate()).strftime("%Y-%m-%d")
        today_day_name = getdate(frappe.utils.nowdate()).strftime("%A")
        delta_day_name = getdate(tprj.last_billing_date).strftime("%A")
        



        dt = last_billed_date.split("-")
        td = today.split("-")
        
        
        
        sd = getdate(tprj.last_billing_date).strftime("%Y-%m-%d")
        ed = ""
        
        
        
        if tprj.billing_frequency == "Weekly":
            if today_day_name == "Monday" and  delta_day_name == "Monday":
                ed = add_to_date(tprj.last_billing_date, days=7,as_string=True)
            elif today_day_name == "Monday" and delta_day_name != "Monday":
                dif = date_diff(today, last_billed_date)
                ed = add_to_date(tprj.last_billing_date, days=dif,as_string=True)

        
        elif tprj.billing_frequency == "Monthly":
            if dt[2] != "01" and td[2] == "01":
                dif = date_diff(today, last_billed_date)
                ed = add_to_date(tprj.last_billing_date, days=dif,as_string=True)
                
            elif dt[2] == "01" and td[2] == "01":
                ed = add_to_date(tprj.last_billing_date, months=1,as_string=True)
                

        
        elif tprj.billing_frequency == "Bi-Monthly":
            if td[2] == "01":
                ed = "{0}-{1}-{2}".format(td[0],td[1],15)
                
            
            if td[2] == "15":
                if td[1] == "12":
                    m = "01"
                else:
                    m = int(td[1]) + 1
                ed = "{0}-{1}-{2}".format(td[0],m,"01")
                

        allocation = frappe.db.sql("""select sum(rai.allocation) as hours from `tabResource Allocation` ra
                                        join `tabResource Allocation Items` rai on rai.parent = ra.name
                                        where rai.project = "{0}" and 
                                        date(ra.date) >= "{1}" and
                                        date(ra.date) <="{2}" and rai.allocation is not null and
                                       (COALESCE(rai.sales_invoice,'')='' AND COALESCE(rai.sales_order,'')='') 
                                        """.format(proj['name'],sd,ed),as_dict=1)
        
        if flt(allocation[0]["hours"])> 0:
            pa=frappe.new_doc("Project Allocation Bill")
            pa.project=tprj.name
            pa.project_name=tprj.project_name
            pa.from_date=sd
            pa.to_date=ed
            alloc=frappe.db.sql("""select rai.task ,sum(rai.allocation) as hours from `tabResource Allocation` ra
                                        join `tabResource Allocation Items` rai on rai.parent = ra.name
                                        where rai.project = "{0}" and 
                                        date(ra.date) >= "{1}" and
                                        date(ra.date) <= "{2}" and rai.allocation is not null 
                                        and (COALESCE(rai.sales_invoice,'')='' AND COALESCE(rai.sales_order,'')='') group by rai.task""".format(proj['name'],sd,ed),as_dict=1)
            
            print(alloc)

            for i in alloc:
                print(i)
                ta=frappe.get_doc("Task",i.get("task"))
                pa.append("items",{
                    "task":i.get("task"),
                    "subject":ta.subject,
                    "allocation_in_hours":i.get("hours")
                })
            pa.save(ignore_permissions=True)
            pa.submit()






from frappe import _
import frappe
from frappe.utils.data import flt
def update_parent_and_project_status(doc, method):

    if doc.status=="Completed":
        if doc.parent_task:
            doc.progress=100
            pt=frappe.db.get_all("Task",{"parent_task":doc.parent_task},["name"])
            tas=[]
            for k in pt:
                task=frappe.get_doc("Task", k.name)
                if task.status=="Completed":
                    tas.append(task.weight)
            if len(tas)>1:
                if sum(tas)==100:
                    parent_task=frappe.get_doc("Task", doc.parent_task)
                    parent_task.progress=100
                    parent_task.status="Completed"
                    parent_task.save(ignore_permissions=True)
                    # if not parent_task.parent_task:
                    #     proj=frappe.get_doc("Project",parent_task.project)
                    #     proj.save(ignore_permisisions=True)
            if len(tas)==1:
                if tas[0]==100:
                    parent_task=frappe.get_doc("Task", doc.parent_task)
                    parent_task.progress=100
                    parent_task.status="Completed"
                    parent_task.save(ignore_permissions=True)
                    # if not parent_task.parent_task:
                    #     proj=frappe.get_doc("Project",parent_task.project)
                    #     proj.save(ignore_permisisions=True)
        

        # if not doc.parent_task:
        #     if doc.project:
        #         pro=frappe.get_doc("Project",doc.project)
        #         pro.save(ignore_permisisions=True)
    if doc.task=="Working":
        doc.progress=50
        if doc.parent_task:
            parent_task=frappe.get_doc("Task", doc.parent_task)
            parent_task.progress=50
            parent_task.save(ignore_permissions=True)
        # doc.save(ignore_permissions=True)

    if doc.task=="Open":
        doc.progress=0
        if doc.parent_task:
            pt=frappe.db.get_all("Task",{"parent_task":doc.parent_task},["name"])
            dc=[]
            parent_task=frappe.get_doc("Task", doc.parent_task)
            for k in pt:
                takc=frappe.get_doc("Task", k.parent_task)
                if takc.status=="open":
                    dc.append(takc.weight)
            if len(dc)>1:
                if sum(dc)!=100:
                    parent_task.status="Inprogress"
                    parent_task.progress=50
                    parent_task.save(ignore_permissions=True)
            if len(dc)==1:
                if dc[0]==100:
                    parent_task.status="Inprogress"
                    parent_task.progress=50
                    parent_task.save(ignore_permissions=True)
            if len(dc)>1:
                if sum(dc)==100:
                    parent_task.status="Open"
                    parent_task.progress=0
                    parent_task.save(ignore_permissions=True)
            if len(dc)==1:
                if dc[0]==100:
                    parent_task.status="Open"
                    parent_task.progress=0
                    parent_task.save(ignore_permissions=True)

        # doc.save(ignore_permissions=True)


def update_project_weight(doc,method):
    if doc.project:
        weight=[]
        xy=frappe.db.get_all("Task",{'project':doc.project,"parent_task":None,"status":"Completed"},["weight"])
        for j in xy:
            weight.append(j.weight)
        proj=frappe.get_doc("Project",doc.project)
        if len(weight)>1:
            proj.weight=sum(weight)
        if len(weight)==1:
            proj.weight=weight[0]
        proj.save(ignore_permissions=True)



def validate_estimate_time(self):
    
    if self.expected_time >0 and self.custom_original_estimated_time==0:
        self.custom_original_estimated_time=self.expected_time

    if len(self.checklist_items)>0:
        if self.status=="Completed":
            for j in self.checklist_items:
                if j.completed==0:
                    frappe.throw("Row {0} :Please Complete Checklist First before Completed Task".format(j.idx))
        hours=[]
        for j in self.checklist_items:
            hours.append(j.hours)
        if sum(hours)/3600!=self.expected_time:
            frappe.throw("Expected Time  {0} And Sum of checklist Item {1} Must be Same ".format(self.expected_time,sum(hours)/3600))



def budget_hours_validatation(self,method):
    
    ex_task=frappe.db.sql("""select * from `tabTask` where name='{}' and is_billable=1 and fixed_cost_based_billing=0""".format(self.name),as_dict=1)

    pr=frappe.get_doc("Project",self.project)
    
    if ex_task:
        new_hr=0.0
        exp_hr=0.0
        for hr in ex_task:
            if self.expected_time < hr.get('expected_time'):
                new_hr=hr.get('expected_time')-self.expected_time
                exp_hr=hr.get('expected_time')
            else:
                new_hr=self.expected_time-hr.get('expected_time')
                exp_hr=hr.get('expected_time')
            if new_hr:
                break

        est_hours=frappe.db.sql("""select sum(expected_time) as hr from `tabTask` 
                        Where project='{0}' and is_billable=1;""".format(self.project),as_dict=1)
        
        for hr in est_hours:
            hrs=0.0
            if self.expected_time < exp_hr:
                hrs=flt(hr.hr)-flt(new_hr)
            else:
                hrs=flt(hr.hr)+flt(new_hr)
            if pr.custom_budget_hours > 0:
                if hrs > pr.custom_budget_hours and self.is_billable==1 and self.fixed_cost_based_billing==0:
                    
                    frappe.throw("The Expected Time (in hours) of {0} hours, is exceeding the Budget Hours on the project. The total hours budgeted on the project is  {1} hours. Please ask the project manager to revise the project budget or consider revising total Expected Time (in hours) for all billable tasks".format(hrs,pr.custom_budget_hours))
                
                else:
                    pr.custom_planned_hours=hrs
                    pr.save(ignore_permissions=True)
        

    else:
        est_hours = frappe.db.sql("""
            SELECT SUM(expected_time) AS hr
            FROM `tabTask`
            WHERE project='{0}' AND is_billable=1 AND name != '{1}'
        """.format(self.project, self.name), as_dict=1)

        pr=frappe.get_doc("Project",self.project)
        # if self.is_billable==1:
        for hr in est_hours:
            hrs=flt(hr.hr)+flt(self.expected_time)
            if pr.custom_budget_hours > 0:
                print(self.fixed_cost_based_billing==1,'self.fixed_cost_based_billing==1')
                if hrs > pr.custom_budget_hours and self.is_billable==1 and self.fixed_cost_based_billing==0:

                    frappe.throw("The Expected Time (in hours) of {0} hours, is exceeding the Budget Hours on the project. The total hours budgeted on the project is  {1} hours. Please ask the project manager to revise the project budget or consider revising total Expected Time (in hours) for all billable tasks".format(hrs,pr.custom_budget_hours))
                else:
                    pr.custom_planned_hours=hrs
                    pr.save(ignore_permissions=True)

    # For Testing Module Design 
@frappe.whitelist()
def status(task):
    task_obj=frappe.get_doc("Task",task)
    if task_obj.custom_test_case:
        test_case_obj = []
        test_case_obj.append(task_obj.custom_test_case)
    elif task_obj.custom_test_case__task:
        test_case_obj = frappe.db.get_list('Test Case',{'task':task_obj.custom_test_case__task}, pluck='name')
    elif task_obj.custom_test_case__project:
        test_case_obj = frappe.db.get_list('Test Case',{'project':task_obj.custom_test_case__project}, pluck='name')
    if task_obj.status == "Pending Review" and task_obj.custom_ignore_testing == 0 and not task_obj.custom_inprogress:
        test_session_obj = frappe.new_doc("Test Session")
        test_session_obj.session_name = task_obj.subject
        test_session_obj.project = task_obj.project
        test_session_obj.task = task_obj.name
        test_session_obj.priority = task_obj.priority
        test_session_obj.session_type = task_obj.custom_session_type
        test_session_obj.company=task_obj.company
        test_session_obj.date=today()
        test_session_obj.environment=task_obj.custom_testing_environment
        for test_case in test_case_obj:
            doc_test_case = frappe.get_doc("Test Case",test_case)
            test_session_obj.append("test_cases",{"test_case": doc_test_case.name,"subject":doc_test_case.subject,"estimated_work":doc_test_case.estimated_work})
        test_session_obj.insert(ignore_permissions=True)
        frappe.db.set_value("Task",task,"custom_inprogress",True)
        frappe.msgprint("Test Session Created Successfully")
            
@frappe.whitelist()
def before_status(task, method=None):
    if task:
        doc=frappe.db.get_all('Task Commit Items',{'parent': task.name},['*'])
        if task.status == "Pending Review" and task.custom_ignore_testing == 0:
            if not task.custom_test_case and not task.custom_test_case__project and not task.custom_test_case__task:
                frappe.throw("Please select 'Test Case' or 'Test Case-Project' or 'Test Case-Task' in <b>Testing Details Section</b>")
            if not task.custom_task_commit_items:
                frappe.throw("Task Commit Items is mandatory")
            if task._doc_before_save.status != task.status:
                if (len(task.custom_task_commit_items) == len(doc)):
                    frappe.throw("Task Commit Items is mandatory")
        if task.status != "Pending Review" and task.custom_inprogress:
            task.custom_inprogress = False



    
@frappe.whitelist(allow_guest=True)
def end_date_validate(self,method):
    timehsheet_settings = frappe.get_doc("Timesheet Settings", "Timesheet Settings")
    max_end_date_changes_allowed = timehsheet_settings.max_end_date_changes_allowed
    role_allowed = timehsheet_settings.role_allowed_to_override_date_change_validation
    all_roles = frappe.get_roles(frappe.session.user)

    if self.exp_end_date != self.get_db_value('exp_end_date'):
        new_exp_end_date = self.exp_end_date

        if not self.custom_previous_exp_date:
            self.custom_previous_exp_date = new_exp_end_date
            previous_changed_date = self.custom_previous_exp_date

        previous_changed_date = self.custom_previous_exp_date

        if previous_changed_date and new_exp_end_date:
            if getdate(new_exp_end_date) > getdate(previous_changed_date):
                if flt(max_end_date_changes_allowed) > 0:
                    if self.custom_end_date_changed_count >= flt(max_end_date_changes_allowed):
                        if role_allowed not in all_roles:
                            msg = f"You have exceeded the maximum number of allowed changes in the 'End Date' for this task. Please contact a person with Role: {role_allowed} to save the changes to the expected end date."
                            frappe.throw(msg)
                self.custom_end_date_changed_count += 1
                self.custom_previous_exp_date = new_exp_end_date
