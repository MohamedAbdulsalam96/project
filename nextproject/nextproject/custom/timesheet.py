import json
from frappe.email.doctype import email_template
from jinja2.nodes import args_as_const
import numpy as np
import frappe
from frappe import _, enqueue, msgprint
from frappe.model.document import Document
from erpnext.projects.doctype.timesheet.timesheet import Timesheet
from frappe.utils import flt, getdate, time_diff_in_hours,add_to_date
from datetime import datetime, timedelta
from erpnext.controllers.queries import get_match_cond
from erpnext.setup.utils import get_exchange_rate
from datetime import date
from frappe.utils import get_datetime
from frappe.utils import add_to_date, flt, get_datetime, getdate, time_diff_in_hours
from frappe.utils.data import get_time, nowdate
from datetime import date, time, datetime

class OverlapError(frappe.ValidationError): pass
class OverWorkLoggedError(frappe.ValidationError): pass
   

def get_activity_cost2(self,method):
    for i in self.time_logs:
        doc1=frappe.db.get_value("Activity Cost",{"activity_type":i.activity_type,"employee":self.employee},["name"])
        if doc1:
            ac=frappe.get_doc("Activity Cost",doc1)
            if self.currency=="INR":
                exchange_rate = get_exchange_rate(ac.custom_currency,self.currency)

                i.costing_rate=flt(ac.costing_rate) * flt(exchange_rate)
                i.costing_amount=flt(ac.costing_rate) * flt(i.billing_hours *flt(exchange_rate))
                i.billing_rate=flt(ac.billing_rate) *flt(exchange_rate)
                i.billing_amount=flt(ac.billing_rate) * flt(i.billing_hours) *flt(exchange_rate)
            else:
                exchange_rate = get_exchange_rate(ac.custom_currency,self.currency)
                i.costing_rate=ac.costing_rate*flt(exchange_rate)
                i.costing_amount=flt(ac.costing_rate) * flt(i.billing_hours)*flt(exchange_rate)
                i.billing_rate= ac.billing_rate
                i.billing_amount=flt(ac.billing_rate) * flt(i.billing_hours)
                i.base_billing_rate=flt(ac.billing_rate) 
                i.base_billing_amount=flt(ac.billing_rate) * flt(i.billing_hours)
        else:
            doc2=frappe.db.get_value("Activity Type",{"activity_type":i.activity_type},["name"])
            if doc2:
                at=frappe.get_doc("Activity Type",doc2)
                if self.currency=="INR":
                    exchange_rate = get_exchange_rate(at.custom_currency,self.currency)

                    i.costing_rate=flt(at.costing_rate) * flt(exchange_rate)
                    i.costing_amount=flt(at.costing_rate) * flt(i.billing_hours *flt(exchange_rate))
                    i.billing_rate=flt(at.billing_rate) *flt(exchange_rate)
                    i.billing_amount=flt(at.billing_rate) * flt(i.billing_hours) *flt(exchange_rate)
                else:
                    exchange_rate = get_exchange_rate(at.custom_currency,self.currency)
                    i.costing_rate=at.costing_rate*flt(exchange_rate)
                    i.costing_amount=flt(at.costing_rate) * flt(i.billing_hours)*flt(exchange_rate)
                    i.billing_rate= at.billing_rate
                    i.billing_amount=flt(at.billing_rate) * flt(i.billing_hours)
                    i.base_billing_rate=flt(at.billing_rate) 
                    i.base_billing_amount=flt(at.billing_rate) * flt(i.billing_hours)



                
      
        

def validate_project(self,method):
    for i in self.time_logs:
        l=frappe.get_doc("Project",i.project)
        if l.is_active=="No" or l.status=="cancelled":
            frappe.throw("Timeheet is not saved because Project {0} is not active or cancelled".format(i.project))
    ts=frappe.get_doc("Timesheet Settings")
    employee=frappe.get_doc("Employee",self.employee)
    roles = frappe.get_roles(employee.user_id)
    role_allowed = False
    if ts.role_allowed_for_overage_timesheet:
        for role in roles:
            if role ==ts.role_allowed_for_overage_timesheet:
                role_allowed = True
                break
    for i in self.time_logs:
        task=frappe.get_doc("Task",i.task)
        tss=frappe.get_doc("Project",task.project)
        if tss.custom_timesheet_overage_allowed>0 and tss.custom_overage_validation_type=="Individual Task":
            doc=frappe.db.sql("""select sum(hours)  as hoa from `tabTimesheet Detail`  where task='{0}' and docstatus in (0,1) """.format(i.task),as_dict=1)
       
            if role_allowed:
                pass
            else:
                if self.get("__islocal"):
                    if ((1+((tss.custom_timesheet_overage_allowed)/100))*task.expected_time) < (flt(doc[0].get("hoa"))+i.hours):
                        frappe.throw(
                            "Maximum allowed time for timesheet entry on task {0} is {1}, you have already filled Timesheet {2} hours. "
                            "{3}"
                        .format(
                            i.task,
                            task.expected_time+(task.expected_time*(tss.custom_timesheet_overage_allowed/100)),
                            flt(doc[0].get("hoa"))+i.hours,
                            "so you cannot fill timesheet More Than" + str(task.expected_time-(task.expected_time+(task.expected_time*(tss.custom_timesheet_overage_allowed/100)))) if task.expected_time-(task.expected_time+(task.expected_time*(tss.custom_timesheet_overage_allowed/100)))>0 else "Timesheet Time Exceed" 
                        ))
                if not self.get("__islocal"):
                    if ((1+((tss.custom_timesheet_overage_allowed)/100))*task.expected_time) < (flt(doc[0].get("hoa"))):
                        frappe.throw(
                            "Maximum allowed time for timesheet entry on task {0} is {1}, you have already fill Timesheet {2} hours. "
                            "{3}"
                        .format(
                            i.task,
                            task.expected_time+(task.expected_time*(tss.custom_timesheet_overage_allowed/100)),
                            flt(doc[0].get("hoa"))+i.hours,
                            "so you cannot fill timesheet More Than" + str(task.expected_time-(task.expected_time+(task.expected_time*(tss.custom_timesheet_overage_allowed/100)))) if task.expected_time-(task.expected_time+(task.expected_time*(tss.custom_timesheet_overage_allowed/100)))>0 else "Timesheet Time Exceed" 
                        ))
        elif tss.custom_timesheet_overage_allowed>0 and tss.custom_overage_validation_type=="Total Project Tasks" and tss.custom_budget_hours > 0:
            est_hours=frappe.db.sql("""select sum(expected_time) as hr from `tabTask` 
                        Where project='{0}'  and is_billable=1;""".format(tss.name),as_dict=1)
           
            doc=frappe.db.sql("""select sum(hours)  as hoa from `tabTimesheet Detail`  where task='{0}' and docstatus in (0,1) """.format(i.task),as_dict=1)
            
            for i in est_hours:
               for j in doc:
                   new_hr=(task.expected_time*(tss.custom_timesheet_overage_allowed/100))+flt(i.hr)
                   if new_hr > tss.custom_budget_hours:
                       frappe.throw("All task of expected time {0} is greater than project budget hours {1} ,so you cannot fill timesheet More Than {2}".
                                    format(new_hr,tss.custom_budget_hours,tss.custom_budget_hours))
                       
                
                            

def progress(self,method):
    for i in self.time_logs:
        f = frappe.get_doc("Task",i.task)
        if f.actual_time and f.expected_time:
            progress_percentage = (f.actual_time / f.expected_time) * 100
            progress = min(progress_percentage, 100)
            f.progress = progress
            f.save(ignore_permissions=True)


            
   

@frappe.whitelist()
def validate_timesheet(self,method):
    for i in self.time_logs:
        doc=frappe.get_doc("Task",i.task)
        if doc.is_billable:
            i.is_billable=1
        doc1=frappe.get_doc("Project",i.project)
        if self.currency != doc1.currency:
            frappe.throw("'{0}' Project Belongs To Differant Currency Please Create Different Timesheet For This project".format(doc1.project_name))


    for j in self.time_logs:
        ts=frappe.get_doc("Timesheet Settings")
        for k in ts.timesheet_settings_items:
            if float(j.hours) in np.arange(k.from_hours,k.to_hours,0.1):
                if len(j.description)<=k.character:
                    frappe.throw("Row {0} : Please Add More Description".format(j.idx))
            




        


        
def set_currency(self,method):
    base_currency = frappe.defaults.get_global_default('currency')
    for i in self.time_logs:
        if i.idx==1:
            doc1=frappe.get_doc("Project",i.project)
            self.currency=doc1.currency


@frappe.whitelist()
def get_activity_cost(employee=None, activity_type=None, currency=None):
	base_currency = frappe.defaults.get_global_default("currency")
	rate = frappe.db.get_values(
		"Activity Cost",
		{"employee": employee, "activity_type": activity_type},
		["costing_rate", "billing_rate"],
		as_dict=True,
	)
	if not rate:
		rate = frappe.db.get_values(
			"Activity Type",
			{"activity_type": activity_type},
			["costing_rate", "billing_rate"],
			as_dict=True,
		)
		if rate and currency and currency != base_currency:
			exchange_rate = get_exchange_rate(base_currency,currency)
			rate[0]["costing_rate"] = rate[0]["costing_rate"] * exchange_rate
			rate[0]["billing_rate"] = rate[0]["billing_rate"] * exchange_rate

	return rate[0] if rate else {}


def timesheet_alert():
    b=[]
    ts=frappe.get_doc("Timesheet Settings")
    tdays=1
    if ts.timesheet_defaulter_in_days:
        tdays=ts.timesheet_defaulter_in_days
    date1= date.today() - timedelta(days=tdays)
    combined_datetime=date1
    emp=frappe.db.get_all("Employee",{'status':'Active'},['name','company_email','employee_name','department','holiday_list','company',"reports_to","default_shift"])
    for h in emp:
        if date1 :
            sd = date1 
            now = getdate(sd)
            dlist = []
            hlist=[]
            if h.holiday_list:
                hlist = frappe.db.get_all("Holiday",{"parent":h.holiday_list},["holiday_date"])
            
            else:
                company=frappe.get_doc("Company",h.company)
                hlist = frappe.db.get_all("Holiday",{"parent":company.default_holiday_list},["holiday_date"])
            
            sh=frappe.db.get_value("Shift Assignment",{"employee":h.name},["shift_type"])
            if sh:
                shift = frappe.get_doc("Shift Type",sh)
                my_time = get_time(shift.start_time)
                combined_datetime = datetime.combine(sd, my_time)
                new_date = combined_datetime + timedelta(hours=int(24))

            elif h.default_shift:
                shift = frappe.get_doc("Shift Type",h.default_shift)
                my_time = get_time(shift.start_time)
                combined_datetime = datetime.combine(sd, my_time)
                new_date = combined_datetime + timedelta(hours=int(24))
            else:
                traceback = frappe.get_traceback()
                frappe.log_error(title = 'Employee Defaulter',message=traceback)
            
            

            for dt in hlist:
                dlist.append(dt.get("holiday_date"))

            wor_hrs=frappe.get_doc("HR Settings")

            
            if now not in dlist:
                parent_doc = frappe.get_doc("Employee", h.name)
                
                tim=frappe.db.sql("""
                    select sum(tl.hours) as total_hours,t.name,
                    t.employee,
                    t.employee_name,
                    emp.department,
                    emp.reports_to,
                    tl.from_time
                    from `tabTimesheet` t 
                    join `tabTimesheet Detail` tl ON t.name = tl.parent
                    join `tabEmployee` emp ON emp.name=t.employee
                    where
                        t.employee='{0}' and
                        tl.from_time between '{1}' and '{2}' and
                        tl.to_time between '{1}' and '{2}' and t.docstatus!=2
                       
                """.format(h.name,combined_datetime,new_date,wor_hrs.standard_working_hours),as_dict=1)
                for o in tim:
                    ts=frappe.get_doc("Timesheet Settings")
                    if flt(o.total_hours)>=ts.min_timesheet_hours:
                            pass
                    if flt(o.total_hours)>0:
                        if flt(o.total_hours)<ts.min_timesheet_hours:
                            lfh = frappe.db.get_value("Leave Application",{"from_date":["<=",date1],"to_date":[">=",date1],"half_day":1},["name"])
                            lf = frappe.db.get_value("Leave Application",{"from_date":["<=",date1],"to_date":[">=",date1],"half_day":0},["name"])

                            if lfh:
                                def_rep=frappe.new_doc("Timesheet Defaulter")
                                def_rep.naming_series="TD.DD..MM..YY..##"
                                def_rep.employee=parent_doc.employee
                                def_rep.employee_name=parent_doc.employee_name
                                def_rep.department=parent_doc.department
                                def_rep.company=parent_doc.company
                                def_rep.date_for_which_hours_are_less=date1
                                def_rep.timesheet_hours=ts.min_timesheet_hours/2
                                def_rep.shortage_hours=(ts.min_timesheet_hours/2)-o.total_hours
                                def_rep.save(ignore_permissions=True)
                            elif lf:
                                pass
                            else:
                                def_rep=frappe.new_doc("Timesheet Defaulter")
                                def_rep.naming_series="TD.DD..MM..YY..##"
                                def_rep.employee=parent_doc.employee
                                def_rep.employee_name=parent_doc.employee_name
                                def_rep.department=parent_doc.department
                                def_rep.company=parent_doc.company
                                def_rep.date_for_which_hours_are_less=date1
                                def_rep.timesheet_hours=ts.min_timesheet_hours/2
                                def_rep.shortage_hours=(ts.min_timesheet_hours/2)-o.total_hours
                                def_rep.save(ignore_permissions=True)

                    if flt(o.total_hours)==0:
                        lfh = frappe.db.get_value("Leave Application",{"from_date":["<=",date1],"to_date":[">=",date1],"half_day":1},["name"])
                        lf = frappe.db.get_value("Leave Application",{"from_date":["<=",date1],"to_date":[">=",date1],"half_day":0},["name"])
                        ts=frappe.get_doc("Timesheet Settings")
                        if lfh:
                            def_rep=frappe.new_doc("Timesheet Defaulter")
                            def_rep.naming_series="TD.DD..MM..YY..##"
                            def_rep.employee=parent_doc.name
                            def_rep.employee_name=parent_doc.employee_name
                            def_rep.department=parent_doc.department
                            def_rep.date_for_which_hours_are_less=date1
                            def_rep.timesheet_hours=0
                            def_rep.shortage_hours=ts.min_timesheet_hours/2
                            def_rep.company=parent_doc.company
                            def_rep.reports_to=parent_doc.reports_to
                            def_rep.save(ignore_permissions=True)
                        elif lf:
                            pass
                        else:
                            def_rep=frappe.new_doc("Timesheet Defaulter")
                            def_rep.naming_series="TD.DD..MM..YY..##"
                            def_rep.employee=parent_doc.name
                            def_rep.employee_name=parent_doc.employee_name
                            def_rep.department=parent_doc.department
                            def_rep.date_for_which_hours_are_less=date1
                            def_rep.timesheet_hours=0
                            def_rep.shortage_hours=ts.min_timesheet_hours/2
                            def_rep.company=parent_doc.company
                            def_rep.reports_to=parent_doc.reports_to
                            def_rep.save(ignore_permissions=True)




                                                            
                    




def set_status():
    doc1=frappe.db.sql("""select name,employee from `tabTimesheet Defaulter` where status='Open'""",as_dict=1)
    for k in doc1:
        try:
            doc=frappe.get_doc("Timesheet Defaulter",k.get("name"))
            emp=frappe.get_doc("Employee",k.get("employee"))
            sh=frappe.db.get_value("Shift Assignment",{"employee":emp.name},["shift_type"])
            if sh:
                shift = frappe.get_doc("Shift Type",sh)
                my_date = doc.date_for_which_hours_are_less
                my_time = get_time(shift.start_time)
                combined_datetime = datetime.combine(my_date, my_time)
                new_date = combined_datetime + timedelta(hours=int(24))

            elif emp.default_shift:
                shift = frappe.get_doc("Shift Type",emp.default_shift)
                my_date = doc.date_for_which_hours_are_less
                my_time = get_time(shift.start_time)
                combined_datetime = datetime.combine(my_date, my_time)
                new_date = combined_datetime + timedelta(hours=int(24))
            else:
                traceback = frappe.get_traceback()
                frappe.log_error(title='Employee Defaulter',message=traceback)

            wor_hrs=frappe.get_doc("HR Settings")
            ab=frappe.db.sql("""
                        select sum(tl.hours) as total_hours,t.name,
                        t.employee,
                        t.employee_name,
                        emp.department,
                        emp.reports_to,
                        tl.from_time
                        from `tabTimesheet` t 
                        join `tabTimesheet Detail` tl ON t.name = tl.parent
                        join `tabEmployee` emp ON emp.name=t.employee
                        where
                            t.docstatus in (0,1) and 
                            t.employee='{0}' and
                            tl.from_time between '{1}' and '{2}' and
                            tl.to_time between '{1}' and '{2}'
                    """.format(emp.name,combined_datetime,new_date,wor_hrs.standard_working_hours),as_dict=1)
            lf = frappe.db.get_value("Leave Application",{"from_date":["<=",my_date],"to_date":[">=",my_date],"half_day":0},["name"])
            if lf:
                doc.timesheet_hours=0
                doc.shortage_hours=0
                doc.status="Closed"
                doc.save(ignore_permissions=True)

            else:
                for db in ab:
                    lfh = frappe.db.get_value("Leave Application",{"from_date":["<=",my_date],"to_date":[">=",my_date],"half_day":1},["name"])
                    if lfh:
                        if flt(db.total_hours)>=(wor_hrs.standard_working_hours/2):
                            doc.timesheet_hours=flt(db.total_hours)
                            doc.shortage_hours=0
                            doc.status="Closed"
                            doc.save(ignore_permissions=True)
                        else:
                            doc.timesheet_hours=flt(db.total_hours)
                            doc.shortage_hours=(wor_hrs.standard_working_hours/2)-flt(db.total_hours)
                            doc.status="Open"
                            doc.save(ignore_permissions=True)
            if flt(db.total_hours)>=flt(wor_hrs.standard_working_hours):
                doc.timesheet_hours=flt(db.total_hours)
                doc.shortage_hours=0
                doc.status="Closed"
                doc.save(ignore_permissions=True)

        except:
            traceback = frappe.get_traceback()
            frappe.log_error(title = 'Timesheet Defaulter Alert',message=traceback)




def timesheet_cancel(self,method):
    val=frappe.db.sql("""select * from `tabFollow up Scrum Items`  fci where timesheet='{0}'""".format(self.name),as_dict=1)
    for i in val:
        if i.get("timesheet"):
            frappe.db.sql("""update `tabFollow up Scrum Items` fci set timesheet="" where name='{0}'""".format(i.get("name")))