import frappe
from datetime import datetime

@frappe.whitelist()
def check_probation_end_date():
    today = datetime.now().date()
    employees = frappe.get_all("Employee", filters={"custom_probation_end_date": today}, fields=['name','employee_name', 'company_email'])
    emails = list(map(lambda x: x.get('company_email'), employees))
    cc_emails = set()
    if employees:
        message=f"Below listed Employees are Probation period concluded today. Please proceed with any necessary evaluations, feedback sessions, or discussions to determine the next steps in their journey within the organization.<br>"
        for idx, employee in enumerate(employees, start=1):
            employee_name = employee.get('name')
            emp_name = employee.get('employee_name')
            message += f"\n {idx}. <b>{employee_name}</b> - {emp_name}\n"

            team_lead = frappe.get_value("Employee", employee_name, "reports_to")
            if team_lead:
                team_lead_email = frappe.get_value("Employee", team_lead, "company_email")
                cc_emails.add(team_lead_email)

                reports_to_employe = frappe.get_value("Employee",team_lead, "reports_to")
                if reports_to_employe:
                    reports_to_employe_email = frappe.get_value("Employee",reports_to_employe, "company_email")
                    cc_emails.add(reports_to_employe_email)

            hr_head_email = get_hr_head_email()
            if hr_head_email:
                cc_emails.add(hr_head_email)

        cc_emails_list = list(cc_emails)
    
        email_args = {
            "recipients":emails,       
            "cc": cc_emails_list,
            "subject": "Probation End Notification",
            "message": message,
        }

        if email_args['recipients'] or email_args['cc']:
            frappe.enqueue(
                method=frappe.sendmail,
                queue="short",
                timeout=300,
                is_async=True,
                delayed = False,
                **email_args,
            )

def get_hr_head_email():
    hr_head = frappe.get_all("Employee",filters={"designation":'HR Head'}, fields=['company_email'])
    if hr_head:
        return hr_head[0]['company_email']