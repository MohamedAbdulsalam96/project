import frappe
from frappe.utils import getdate

def cal_dt():
    get_tk = frappe.db.get_all("Task",{"status" :["not in" ,["Template","Cancelled"]]},["name"])
    # print("bif***************************",get_tk)
    if get_tk :

        for i in get_tk:
            tkn = frappe.get_doc("Task",i.get("name"))
            if tkn.exp_start_date and tkn.exp_end_date and tkn.expected_time:
                sd = tkn.exp_start_date
                ed = tkn.exp_end_date
                now = getdate(sd)
                now1= getdate(ed)

                Days =  (now1 -now).days + 1

                tkn.total_duration_in_days = Days

                dh = float(tkn.expected_time)/Days

                tkn.duration_per_day_in_hours = dh

                tkn.save(ignore_permissions = True)
            else:
                pass