# # from multiprocessing.spawn import prepare
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import flt
import json

@frappe.whitelist()
def fetch_timesheet(employee, from_date, to_date, project=None):
    filters={} 
    prepared_data=[]
    
    timesheet_list = frappe.db.get_all('Timesheet', {
    "employee": employee,
    "docstatus": 0,
    "approved":0,
    "start_date": ["between", [from_date, to_date]],
    "end_date": ["between", [from_date, to_date]]
    }, ["name"])
    if len(timesheet_list)==0:
        frappe.throw("No timesheet entries found for the employee {0} for the date range {1} and {2}".format(employee,from_date,to_date))
    for sheet in timesheet_list:
        if project:
            filters.update({
                "parent":sheet.name,
                "project":project,
                "approved":0

            })
        else:
            filters.update({
                "parent":sheet.name
            })
            
        data= frappe.db.get_all("Timesheet Detail", filters, ['*'])
        for d in data:
            task=frappe.get_doc("Task",d.task)
            d.update({"subject":task.subject})
            d.update({"expected_time":task.expected_time,"actual_time":task.actual_time,"progress":task.progress})
            doc=frappe.db.sql("""select sum(hours)  as hoa from `tabTimesheet Detail`  where task='{0}' and docstatus in (0,1) """.format(d.task),as_dict=1)
            for k in doc:
                d.update({"remaining_time":flt(task.expected_time)-flt(k.get("hoa"))})
            prepared_data.append(d)
           
    return prepared_data



@frappe.whitelist()
def make_task(source_name, target_doc=None):
	return get_mapped_doc("HD Ticket", source_name, {"HD Ticket": {"doctype": "Task","ticket":source_name}}, target_doc)


@frappe.whitelist()
def make_invoice(source_name, target_doc=None):
	return get_mapped_doc("HD Ticket", source_name, {"HD Ticket": {"doctype": "Sales Invoice","ticket":source_name}}, target_doc)


# create by satish

@frappe.whitelist()
def custom_submit_hd_ticket(doc,values):
    hd=frappe.get_doc("HD Ticket",doc)
    print("hhhhhhhhhhhhhhh",hd)
    new_record = frappe.new_doc("Task")
    obj = json.loads(values)
    

    new_record.subject = obj.get('subject')
    new_record.project = obj.get('project')
    new_record.company = obj.get('company')
    new_record.exp_start_date = obj.get('exp_start_date')
    new_record.exp_end_date = obj.get('exp_end_date')
    new_record.expected_time = obj.get('expected_time')  
    new_record.priority = obj.get('priority')
    new_record.fixed_cost_based_billing = obj.get('fixed_cost_billing')
    new_record.type = obj.get('type')  
    new_record.department = obj.get('department')
    new_record.is_billable = obj.get('is_billable')
    new_record.parent_task = obj.get('parent_task')
    new_record.employee_group = obj.get('employee_group')
    new_record.primary_consultant = obj.get('primary_consultant')
    new_record.actual_time = obj.get('estimated_hour')
    new_record.estimated_hour=obj.get("estimated_hour")
    new_record.ticket=hd.name
    new_record.description=hd.description
    new_record.insert(ignore_permissions=True)

    return new_record.name

@frappe.whitelist(allow_guest = True)
def get_all_sales_partner_list():
    doc = frappe.db.get_all('Sales Partner',{"show_in_website":1})
    record_list = []
    for i in doc:
        rec = frappe.get_doc('Sales Partner', i.name)
        domains = [domain.domain for domain in rec.custom_domain]
        details = {
            'partner_name':rec.partner_name,
            'territory':rec.territory,
            'custom_certified_partner':rec.custom_certified_partner,
            'logo':rec.logo,
            'partner_type': rec.partner_type,
            'custom_domain': domains

        }
        record_list.append(details)
    return record_list


@frappe.whitelist(allow_guest = True)
def sales_partner_details(name):
    # name = 'James%20Watson'
    # dyanamic_link = frappe.get_all("Dynamic Link",{'link_doctype':'Sales Partner'})
    # print(dyanamic_link.link_name)
    
    doc = frappe.get_doc('Sales Partner',name)
    # contact = get_contact_number(name)
    # address = get_address_details(name)
    contact_and_address_details = get_contact_and_address_details(name)
    return {'details':doc,
            'contact_and_address_details':contact_and_address_details}

# @frappe.whitelist(allow_guest = True)
# def sales_partner_email(name):
#     # name = 'James%20Watson'
#     # dyanamic_link = frappe.get_all("Dynamic Link")
#     # print(dyanamic_link)
#     doc = frappe.get_doc('Contact',name)
#     return doc
     
@frappe.whitelist(allow_guest = True)
def sales_partner_type_list():
    
    doc = frappe.db.get_all('Sales Partner Type')
    sales_list = []
    for i in doc:
        # rec = frappe.get_doc('Sales Partner Type', i.name)
        sales_list.append(i.name)
       
    return sales_list


@frappe.whitelist(allow_guest = True)
def sales_partner_domain_list():
    
    doc = frappe.db.get_all('Domain')
    domain_list = []
    for i in doc:
        # rec = frappe.get_doc('Sales Partner Type', i.name)
        domain_list.append(i.name)
       
    return domain_list


@frappe.whitelist(allow_guest=True)
def get_contact_number():
    sale_partner_name = 'James%20Watson'
    contact = {"phone_nos" :[],
    "email_id" : []
    }
    link = frappe.get_all('Dynamic Link',{'link_doctype':'Sales Partner','link_name':sale_partner_name,'parenttype':'Contact'},['parent'])
    for i in link:

        contact_doc = frappe.get_doc('Contact',i.parent)
        for email in contact_doc.email_ids:
            contact['email_id'].append(email.email_id)
        for no in contact_doc.phone_nos:
            contact['phone_nos'].append(no.phone)
    return contact
















    # doc = frappe.get_all("Contact")
    # contact = {"phone_nos" :[],
    # "email_id" : []
    # }

    # for i in doc:
        
    #     rec = frappe.get_doc('Contact',i)
    #     print(rec.name)
    #     for sale in rec.links:
    #         print(sale.link_name)
    #         if sale.link_doctype == 'Sales Partner' and sale.link_name == sale_partner_name:
    #             for email in rec.email_ids:
    #                 contact['email_id'].append(email.email_id)
    #             for no in rec.phone_nos:
    #                 contact['phone_nos'].append(no.phone)
    #         break  
    #     print(contact)
            
    # return contact   


@frappe.whitelist(allow_guest=True)
def get_address_details():
    sale_partner_name = 'James%20Watson'
    contact = {"address_details" : []
    }


    link = frappe.get_all('Dynamic Link',{'link_doctype':'Sales Partner','link_name':sale_partner_name,'parenttype':'Address'},['parent'])
    for i in link:

        address_doc = frappe.get_doc('Address',i.parent)
        contact["address_details"].append({
                                    "address_title": address_doc.address_title,
                                    "address_line1":address_doc.address_line1, 
                                    "address_line2":address_doc.address_line2,
                                    "city":address_doc.city,
                                    "county":address_doc.county,
                                    
                                    "state": address_doc.state,
                                    "pincode": address_doc.pincode,
                                    "email_id": address_doc.email_id,
                                    "phone": address_doc.phone,
                                    "fax": address_doc.fax,
                                    "tax_category": address_doc.tax_category})

        print(contact)
    return contact

















    # doc = frappe.get_all("Address")
    # contact = {"address_details" : []
    # }

    # for i in doc:
        
    #     rec = frappe.get_doc('Address',i)
    #     print(rec.name)
    #     for sale in rec.links:
    #         print(sale.link_name)
    #         if sale.link_doctype == 'Sales Partner' and sale.link_name == sale_partner_name:
    #             contact["address_details"].append({
    #                                                 "address_title": rec.address_title,
    #                                                 "address_line1":rec.address_line1, 
    #                                                 "address_line2":rec.address_line2,
    #                                                 "city":rec.city,
    #                                                 "county":rec.county,
                                                    
    #                                                 "state": rec.state,
    #                                                 "pincode": rec.pincode,
    #                                                 "email_id": rec.email_id,
    #                                                 "phone": rec.phone,
    #                                                 "fax": rec.fax,
    #                                                 "tax_category": rec.tax_category})
              
    #     print(contact)
            
    # return contact   





@frappe.whitelist(allow_guest=True)
def get_contact_and_address_details(sale_partner_name):
    # sale_partner_name = 'James%20Watson'
    contact_and_address_details = {"phone_nos" :[],
    "email_id" : [],
    "address_details" : []
    }

    link = frappe.get_all('Dynamic Link',{'link_doctype':'Sales Partner','link_name':sale_partner_name},['parent','parenttype'])
    for i in link:

        if i.parenttype == 'Address':

            address_doc = frappe.get_doc('Address',i.parent)
            contact_and_address_details["address_details"].append({
                                        "address_title": address_doc.address_title,
                                        "address_line1":address_doc.address_line1, 
                                        "address_line2":address_doc.address_line2,
                                        "city":address_doc.city,
                                        "county":address_doc.county,
                                        
                                        "state": address_doc.state,
                                        "pincode": address_doc.pincode,
                                        "email_id": address_doc.email_id,
                                        "phone": address_doc.phone,
                                        "fax": address_doc.fax,
                                        "tax_category": address_doc.tax_category})

        elif i.parenttype == 'Contact':

            contact_doc = frappe.get_doc('Contact',i.parent)
            for email in contact_doc.email_ids:
                contact_and_address_details['email_id'].append(email.email_id)
            for no in contact_doc.phone_nos:
                contact_and_address_details['phone_nos'].append(no.phone)
    return contact_and_address_details