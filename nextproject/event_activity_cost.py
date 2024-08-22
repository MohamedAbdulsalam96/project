from datetime import date
import frappe
from frappe.utils.data import flt


@frappe.whitelist()
def activity_cost(employee):
    hr=frappe.get_doc("HR Settings")
    salary_structure = frappe.get_value(
        "Salary Structure Assignment",
        {
            "employee": employee,
            "from_date": ("<=", date.today()),
            "docstatus": 1,
        },
        "name",
        order_by="from_date desc",
        as_dict=True,
    )


    if salary_structure:
        ss=frappe.get_doc("Salary Structure Assignment",salary_structure)
        costing_rate=(flt(ss.base)+flt(ss.variable))/(22*flt(hr.standard_working_hours))
        return costing_rate



def set_cost(self,method):
    hr=frappe.get_doc("HR Settings")
    salary_structure_assignment = frappe.get_value(
        "Salary Structure Assignment",
        {
            "employee": self.employee,
            "from_date": ("<=", date.today()),
            "docstatus": 1,
        },
        "name",
        order_by="from_date desc",
        as_dict=True,
    )


    if salary_structure_assignment:
        ss=frappe.get_doc("Salary Structure Assignment",salary_structure_assignment)
        costing_rate=(flt(ss.base)+flt(ss.variable))/(22*flt(hr.standard_working_hours))
        if flt(self.costing_rate)==0:
            self.costing_rate=costing_rate

    if self.employee:
        doc=frappe.get_doc("Employee",self.employee)
        cuu=frappe.db.get_value("Company",{"name":doc.company},["default_currency"])
        if cuu:
            self.custom_currency=cuu


