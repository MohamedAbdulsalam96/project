import frappe

@frappe.whitelist(allow_guest=True)
def create_lead(contact_name=None, contact_number=None,contact_skype=None, contact_notes=None, contact_email=None,referral_code=None):
    lead = frappe.new_doc("Lead")

    if contact_name:
        split_name = contact_name.split(" ")    
        lead.first_name = split_name[0]
        lead.last_name = split_name[-1]
    else:
        raise ValueError("contact_name is missing")

    if contact_number:
        lead.mobile_no = contact_number
        lead.phone = contact_number
    else:
        raise ValueError("contact_number is missing")

    if contact_email:
        lead.email_id = contact_email
    else:
        raise ValueError("contact_email is missing")

    lead.custom_sales_partner = frappe.db.get_value('Sales Partner', {'referral_code':referral_code}, 'name')

    try:
        lead.insert(ignore_permissions=True)
        print("*****lead.name ***********",lead.name)
        return lead.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),("Failed to create lead"))
        return {"exc": str(e)}

