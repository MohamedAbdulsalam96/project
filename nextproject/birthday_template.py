import frappe
from frappe.model.document import Document
from datetime import datetime

from frappe.utils.data import getdate

class SendBirthdayEmail():
    @classmethod
    def get_today_employee(cls):
        today=getdate(datetime.today())
        all_employees = frappe.get_all('Employee', filters={'status': 'Active'}, fields=['name','employee_name', 'company_email', 'date_of_birth'])
        employees_today = [employee for employee in all_employees if getdate(employee['date_of_birth'])== today]
        return employees_today
   
    @classmethod
    def send_email(cls):
        
        today_employee=SendBirthdayEmail.get_today_employee()
    
        if today_employee:
            for x in today_employee:
                emails=list(map(lambda x:x.get('company_email'),frappe.get_all('Employee',filters={'status':'Active','company_email': ('not in', [x.get('company_email')])},fields=['company_email'])))                
                email_args = {
                              "recipients": x.get('company_email'),
                                "subject": 'Birthday Reminder',
                                "cc":emails,
                                "template":'birthday_template',
                                'args':{"doc":frappe.get_doc("Employee",x.get('name'))},
                            }

                frappe.enqueue(
                        method=frappe.sendmail,
                        queue="short",
                        timeout=300,
                        event=None,
                        is_async=True,
                        job_name="Birthday Notification",
                        now=False,
                        **email_args,
                    )

@frappe.whitelist()   
def excute_send_email():
    doc=frappe.get_doc('Email Template Setting')
    if doc.enabled_tempate==1:
        SendBirthdayEmail.send_email()
    
