import frappe



@frappe.whitelist()
def get_customer_contacts(name):
    contacts = {}
    cnp = []
    cp =[]
    eids = frappe.db.sql("""
                         select  ect.email_id as npe from `tabContact` ct
                         join `tabDynamic Link` dl on dl.link_name = '{0}' and dl.parent = ct.name
                         join `tabContact Email` ect on ect.parent = ct.name 
                            """.format(name),as_dict=1)
    if eids:
        for emails in eids:
            cnp.append(emails.get("npe"))
            
        
        contacts.update({
            "primary":set(cnp),
            "nprimary":set(cnp)
        })
        

        print("sjnv  v**********************",contacts)
        return contacts

@frappe.whitelist()
def get_lead_contacts(name):
    lcontacts = []
    lead = frappe.get_doc("Lead",name)
    if lead.email_id:
       lcontacts.append(lead.email_id)
       return lcontacts
    else:
        frappe.msgprint("No Email Id Found in Lead - {0}. Please Enter Email Manually".format(name))

