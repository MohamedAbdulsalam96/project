# Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class PerformanceTargetVariable(Document):
    def before_save(self):
        total_weightage = 0
        for item in self.performance_target_variable_items:
            total_weightage += item.weightage_

        if total_weightage != 100:
            frappe.throw("Total weightage must be 100% before saving the document.")


