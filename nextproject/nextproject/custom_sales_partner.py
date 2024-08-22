
import frappe
import string
import random


@frappe.whitelist(allow_guest=True)
def validate(self,method):
    base=frappe.utils.get_url()
    print("base"*36,base)
    link = f"{base}/book_appointment/?referral_code={self.referral_code}"
    self.custom_referral_link = link
    # frappe.msgprint(msg)


@frappe.whitelist(allow_guest=True)
def code_generator():
    existing_codes = frappe.db.sql("""
    SELECT referral_code FROM `tabSales Partner`
    """)

    print("*Existing codes  :",existing_codes )

    existing_codes = [code[0] for code in existing_codes]
    code_length = 8
    characters = string.ascii_uppercase

    while True:
        new_code = ''.join(random.choices(characters, k=code_length))
        if new_code not in existing_codes:
            break
        # self.referral_code = new_code
    return new_code