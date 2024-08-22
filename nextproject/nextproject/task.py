
from __future__ import unicode_literals
import frappe
from frappe import _
from six import iteritems
from email_reply_parser import EmailReplyParser
from frappe.utils import (flt, getdate, get_url, now,
                          nowtime, get_time, today, get_datetime, add_days, datetime)
from erpnext.controllers.queries import get_filters_cond
from frappe.desk.reportview import get_match_cond
from erpnext.hr.doctype.daily_work_summary.daily_work_summary import get_users_email
from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday
from frappe.model.document import Document
from datetime import datetime


@frappe.whitelist()
def daily():

    # for billing based on milestone
    project = frappe.db.sql(""" select name from `tabProject`
                                where billing_based_on = 'Milestone Based' and status = "Open"
                                """,
                                as_dict= True)

    for proj in project:
        Prj = frappe.get_doc("Project",proj['name'])
        doctype = Prj.auto_creation_doctype
        SI = frappe.new_doc(doctype)
        if doctype == "Sales Order":
            SI.delivery_date = frappe.utils.nowdate()
        SI.customer = Prj.customer
        SI.currency = Prj.currency
        SI.due_date = frappe.utils.nowdate()
        SI.project = Prj.name
        project_list_task = frappe.db.sql(""" select milestone,billing_item,billing_percentage from `tabProject Milestone Child` 
                                            where progress = 100 and (s_order is NULL) and parent = %(proj)s 
                                            and (invoice is NULL)""",{'proj':proj['name']},as_dict=True)
        for task in project_list_task:
            SI.append("items", {
                "item_code": task["billing_item"],
                "qty": 1,
                "rate": ((Prj.total_project_value_excluding_taxes * task["billing_percentage"]) / 100),
                "conversion_factor": 1,
            })
        if len(project_list_task) > 0:
            SI.insert()
            SI.save()
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
                                    where billing_based_on = 'Fixed Recurring' and status = "Open"
                                    """,as_dict=True)
    for proj in recc_project:
        prj = frappe.get_doc("Project", proj['name'])
        if prj.billing_frequency == "Daily":
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.delivery_date = frappe.utils.nowdate()
            SI.customer = prj.customer
            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.append("items", {
                "item_code": prj.recurring_item,
                "qty": 1,
                "rate": prj.recurring_charges,
                "conversion_factor": 1,
            })
            SI.insert()
            SI.save()
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
        print("*******************************************************************",delta.days)
        if prj.billing_frequency == "Weekly" and int(delta.days) >= 7 or prj.billing_frequency == "Monthly" and int(delta.days) >= 30 or prj.billing_frequency == "Bi-Yearly" and int(delta.days) >= 180 or prj.billing_frequency == "Yearly" and int(delta.days) >= 360:
            doctype = prj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.delivery_date = frappe.utils.nowdate()
            SI.customer = prj.customer
            SI.currency = prj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = prj.name
            SI.append("items", {
                "item_code": prj.recurring_item,
                "qty": 1,
                "rate": prj.recurring_charges,
                "conversion_factor": 1,
            })
            SI.insert()
            SI.save()
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

        # if prj.billing_frequency == "Custom":
        #     lst = str(frappe.utils.nowdate()).split("-")
        #     print("***********************************************************",lst[2])


#     timesheet based

    time_project = frappe.db.sql(""" select name from `tabProject`
                                                where billing_based_on = 'Timesheet Based' and status = "Open"
                                                """, as_dict=True)
    for proj in time_project:
        tprj = frappe.get_doc("Project", proj['name'])
        delta = getdate(frappe.utils.nowdate()) - tprj.start_date
        if tprj.billing_frequency == "Weekly" and int(delta.days) >= 7 or tprj.billing_frequency == "Monthly" and int(
                delta.days) >= 30 or tprj.billing_frequency == "Bi-Yearly" and int(
            delta.days) >= 180 or tprj.billing_frequency == "Yearly" and int(delta.days) >= 360:
            doctype = tprj.auto_creation_doctype
            SI = frappe.new_doc(doctype)
            if doctype == "Sales Order":
                SI.delivery_date = frappe.utils.nowdate()
            SI.customer = tprj.customer
            SI.currency = tprj.currency
            SI.due_date = frappe.utils.nowdate()
            SI.project = tprj.name
            SI.company = tprj.company
            abs_val = 0
            timesheet = list(frappe.db.sql(""" select parent from `tabTimesheet Detail` where project = %(proj)s and sales_invoice is NULL
                                                    and sales_order is NULL""",
                                           {'proj': proj['name']}))

            print("timesheet*******************************************", timesheet)
            lst = []
            for tsheet in set(timesheet):
                print("tsheet*******************************************", tsheet[0])
                ttsheet_obj = frappe.get_doc("Timesheet", tsheet[0])

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
                            # accounts = frappe.db.get_values("Company", {"company_name": tprj.company}, ["default_income_account", "cost_center"], as_dict=True)
                            # print("***************************************************accounts*********",accounts)
                            SI.append("items", {
                                "item_code": tprj.timesheet_item,
                                "qty": hours,
                                "rate": billing_rate,
                                "conversion_factor": 1

                            })
                            if doctype == "Sales Invoice":
                                SI.append("timesheets", {
                                    "time_sheet": tsheet_obj.name,
                                    "billing_hours": hours,
                                    "billing_amount": billing_amount,
                                })
                            lst.append(tsheet_obj.name)

            if abs_val == 1:
                SI.insert()
                SI.save()
                SI.flags.ignore_validate_update_after_submit = True
                if tprj.auto_submit_invoice == 1 or tprj.auto_submit_order == 1:
                    SI.submit()
                    print("********************************lst", lst)
                    for time_sheet in set(lst):
                        timesheet_obj = frappe.get_doc("Timesheet", time_sheet)
                        hours = flt(timesheet_obj.total_billable_hours) - flt(timesheet_obj.total_billed_hours)
                        billing_amount = flt(timesheet_obj.total_billable_amount) - flt(
                            timesheet_obj.total_billed_amount)
                        if hours > 0:
                            billing_rate = billing_amount / hours
                        timesheet_obj.per_billed = (billing_amount * 100) / timesheet_obj.total_billable_amount
                        if timesheet_obj.per_billed == 100:

                            frappe.db.sql(
                                """ update `tabTimesheet` set total_billed_amount = %(total_billed_amount)s, per_billed= %(per_billed)s,
                                  status = "Billed",total_billed_hours = %(hours)s where name = %(name)s""",
                                {'total_billed_amount': billing_amount, 'name': timesheet_obj.name,
                                 'per_billed': timesheet_obj.per_billed,
                                 'hours': hours})
                            frappe.db.commit()
                            if tprj.auto_creation_doctype == "Sales Invoice":
                                frappe.db.sql(
                                    """ update `tabTimesheet Detail` set sales_invoice = %(name)s where parent = %(parent)s""",
                                    {'parent': timesheet_obj.name, 'name': SI.name})
                                frappe.db.commit()
                            if tprj.auto_creation_doctype == "Sales Order":
                                frappe.db.sql(
                                    """ update `tabTimesheet Detail` set sales_order = %(name)s where parent = %(parent)s""",
                                    {'parent': timesheet_obj.name, 'name': SI.name})
                                frappe.db.commit()
                        else:
                            frappe.db.sql(
                                """ update `tabTimesheet` set total_billed_amount = %(total_billed_amount)s, per_billed= %(per_billed)s,
                                 total_billed_hours = %(hours)s where name = %(name)s""",
                                {'total_billed_amount': billing_amount, 'name': timesheet_obj.name,
                                 'per_billed': timesheet_obj.per_billed,
                                 'hours': hours})
                            frappe.db.commit()

                            if tprj.auto_creation_doctype == "Sales Invoice":
                                frappe.db.sql(
                                    """ update `tabTimesheet Detail` set sales_invoice = %(name)s where parent = %(parent)s""",
                                    {'parent': timesheet_obj.name, 'name': SI.name})
                                frappe.db.commit()
                            if tprj.auto_creation_doctype == "Sales Order":
                                frappe.db.sql(
                                    """ update `tabTimesheet Detail` set sales_order = %(name)s where parent = %(parent)s""",
                                    {'parent': timesheet_obj.name, 'name': SI.name})
                                frappe.db.commit()

    
    
        
        





# def create_item_variant(self,method):
#     if not self.is_new():
#         if self.item_code and self.is_template==0:
#             itemdoc=frappe.get_doc("Item",self.item_code)
#             if itemdoc.has_variants==1:
#                 if self.project:
#                     ip=frappe.get_doc("Project",self.project)
#                     if ip.scope_of_supply:
#                         scopedoc=frappe.get_doc("Scope of Supply",ip.scope_of_supply)
#                         self.item_code=scopedoc.name+"-"+str(self.item_code)
#         if self.project:
#             ipc=frappe.get_doc("Project",self.project)
#             if ipc.scope_of_supply:
#                 scopedoc1=frappe.get_doc("Scope of Supply",ipc.scope_of_supply)
#                 for i in scopedoc1.project_milestone_list:
#                     if i.is_billable:
#                         frappe.db.sql("""update `tabProject Milestone` 
# 									SET task = '{0}' where item_code='{1}' and parent='{2}'""".format(self.name,self.item_code,scopedoc1.name))
#                         frappe.db.sql("""update `tabSOS Budget Items` 
# 									SET task = '{0}' where item_code='{1}' and parent='{2}' """.format(self.name,self.item_code,scopedoc1.name))
#                         if self.item_code==i.item_code:
#                             self.revenue_budget=str(i.billing_amount)
                


        



