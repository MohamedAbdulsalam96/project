import frappe


def execute():
    pr=frappe.get_all('Project',['name'])
    for i in pr:
        est_hours=frappe.db.sql("""select sum(expected_time) as hr from `tabTask` 
                        Where project='{0}' and is_billable=1 and status  NOT IN ('Cancelled','Template');;""".format(i.get('name')),as_dict=1)
        prj=frappe.get_doc('Project',i.get('name'))
        prj.custom_planned_hours=est_hours[0].get('hr')
        prj.save(ignore_permissions=True)