import frappe



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
            # cp.append(emails.get("pe"))
        
        contacts.update({
            "primary":set(cnp),
            "nprimary":set(cnp)
        })
        

        print("sjnv  v**********************",contacts)
        return contacts