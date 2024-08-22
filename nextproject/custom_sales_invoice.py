from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
import frappe

class CustomSalesInvoice(SalesInvoice):
    @frappe.whitelist()
    def update_timesheet_billing_for_project(self):
        if not self.timesheets and self.project and self.ignore_timesheets == 0:
            self.add_timesheet_data()
        else:
            self.calculate_billing_amount_for_timesheet()

    def before_cancel(self):
        if self.project:
            doc=frappe.get_doc("Project",self.project)
            if doc.billing_based_on =='Milestone Based':
                for i in doc.milestone:
                    if self.name==i.invoice:
                        i.db_set("invoice","")
                        frappe.db.commit()
        self.check_if_consolidated_invoice()

        super(SalesInvoice, self).before_cancel()
        self.update_time_sheet(None)


@frappe.whitelist()
def get_contacts(name):
    contacts = {}
    cnp = []
    cp =[]
    eids = frappe.db.sql("""
                         select  ect2.email_id  as pe, ect.email_id as npe from `tabContact` ct
                         join `tabDynamic Link` dl on dl.link_name = '{0}' and dl.parent = ct.name
                         join `tabContact Email` ect on ect.parent = ct.name and ect.is_primary = 0
                         join `tabContact Email` ect2 on ect2.parent = ct.name and ect2.is_primary = 1
                            """.format(name),as_dict=1)
    if eids:
        for emails in eids:
            cnp.append(emails.get("npe"))
        
        contacts.update({
            "primary":set(cnp),
            "nprimary":set(cnp)
        })
        
        return contacts
