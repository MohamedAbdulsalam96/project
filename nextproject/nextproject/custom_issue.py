import frappe
from frappe import _

from erpnext.setup.utils import get_exchange_rate
from frappe.utils.data import flt
from frappe.model.document import Document



def currency_update(self,method):
    base_currency = frappe.defaults.get_global_default('currency')    
    if self.currency!="INR":
        exchange_rate = get_exchange_rate(base_currency,self.currency)
        self.base_estimated_cost=flt(self.estimated_cost)*flt(exchange_rate)
    per = (flt(self.estimated_cost) *18 /100)
    gst = flt(self.estimated_cost) + per
    self.grand_total=gst
    if flt(self.estimated_cost) > 0:
        self.estimated_cost_in_words = frappe.utils.money_in_words(self.estimated_cost, self.currency)
    if flt(self.grand_total) > 0:
        self.grand__total_cost_in_words = frappe.utils.money_in_words(gst, self.currency)



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
            cp.append(emails.get("pe"))
        
        contacts.update({
            "primary":set(cp),
            "nprimary":set(cnp)
        })
        

        print("sjnv  v**********************",contacts)
        return contacts


def get_price(self,method):
    if self.issue_type == "Customisation Request":
        proj = frappe.get_doc("Project",{'name':self.project})

        if proj.price_list:
            doc=frappe.get_value("Item Price",{'item_code':proj.cr_item,'price_list':proj.price_list},["name"])
            if doc:
                i = frappe.get_doc("Item Price",{'item_code':proj.cr_item,'price_list':proj.price_list})
                if flt(self.estimated_hours)>0:
                    self.estimated_cost=flt(i.price_list_rate)*(flt(self.estimated_hours)/3600)
        else:
            j=frappe.get_doc("Customer",{'name':proj.customer})
            doc=frappe.get_value("Item Price",{'item_code':proj.cr_item,'price_list':proj.price_list},["name"])
            if doc:
                i = frappe.get_doc("Item Price",{'item_code':proj.cr_item,'price_list':j.default_price_list})
                if flt(self.estimated_hours)>0:
                    self.estimated_cost=flt(i.price_list_rate)*(flt(self.estimated_hours)/3600)