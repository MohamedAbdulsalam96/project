# from __future__ import unicode_literals
# import frappe
# from frappe import _
# from frappe.model.document import Document
# class DuplicationError(frappe.ValidationError): pass
# from erpnext.projects.doctype.activity_cost.activity_cost import  ActivityCost

# class CustomToDo(ActivityCost):
#     def validate(self):
#         super(CustomToDo, self).validate()


#     def check_unique(self):
#         if self.project:
#             if frappe.db.sql(
#                     """select name from `tabActivity Cost` where employee_name= %s and activity_type= %s and name != %s 
#                     and project = %s""",
#                     (self.employee_name, self.activity_type, self.name, self.project)):
#                 frappe.throw(_("Activity Cost exists for Employee {0} against Activity Type - {1} for Project {2}")
#                              .format(self.employee, self.activity_type, self.project), DuplicationError)

#         elif self.employee:
#             if frappe.db.sql(
#                     """select name from `tabActivity Cost` where employee_name= %s and activity_type= %s and name != %s""",
#                     (self.employee_name, self.activity_type, self.name)):
#                 frappe.throw(_("Activity Cost exists for Employee {0} against Activity Type - {1}")
#                              .format(self.employee, self.activity_type), DuplicationError)
#         else:
#             if frappe.db.sql(
#                     """select name from `tabActivity Cost` where ifnull(employee, '')='' and activity_type= %s and name != %s""",
#                     (self.activity_type, self.name)):
#                 frappe.throw(_("Default Activity Cost exists for Activity Type - {0}")
#                              .format(self.activity_type), DuplicationError)
