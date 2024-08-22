import frappe
from  hrms.payroll.doctype.salary_slip import salary_slip
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint

@frappe.whitelist()
def employee_find(self,method=None):
    s= frappe.db.get_value("Salary Structure Assignment",{"employee":self.custom_employee},["employee","salary_structure"])
    if s:
        self.custom_salary_structure=s[1]
        self.custom_earnings=[]
        self.custom_deduction=[]
        make_salary_slip(self,self.custom_salary_structure,target_doc=None,
        employee=self.custom_employee,
        posting_date=None,
        as_print=False,
        print_format=None,
        for_preview=0,)
    else:
        frappe.throw("No Salary Structure")


@frappe.whitelist()
def make_salary_slip(
    self,
    source,
    target_doc=None,
    employee=None,
    posting_date=None,
    as_print=False,
    print_format=None,
    for_preview=0,
    
):
    def postprocess(source,target):
        if employee:
            target.employee = employee
            if posting_date:
                target.posting_date = posting_date

        target.run_method("process_salary_structure", for_preview=for_preview)

    doc = get_mapped_doc(
        "Salary Structure",
        source,
        {
            "Salary Structure": {
                "doctype": "Salary Slip",
                "field_map": {
                    "total_earning": "gross_pay",
                    "name": "salary_structure",
                    "currency": "currency",
                },
            }
        },
        target_doc,
        postprocess,
        ignore_child_tables=True,
        #ignore_permissions=ignore_permissions,
        cached=True,
    )
    total_amount = 0
    total=0
    if doc:
        for i in doc.earnings:
            self.append("custom_earnings",{'component':i.salary_component,'amount':i.amount})
            total_amount+=i.amount
        for j in doc.deductions:
            self.append("custom_deduction",{'component':j.salary_component,'amount':j.amount})
            total+=j.amount
        self.custom_total_earnings=total_amount
        self.custom_total_deductions=total
        return doc
        
   
    








	