# Copyright (c) 2022, Dexciss and contributors
# For license information, please see license.txt
from erpnext.setup.utils import get_exchange_rate
import frappe
from frappe.utils.data import flt


def execute(filters=None):
	columns = columns_rep()
	c = conditions(filters)
	data = query(filters, c)
	chart = get_chart_data(data)
	return columns, data ,None, chart



def conditions(filters):
	condition = ""
	if filters.get("company"):
		company = filters.get("company")
		condition+=(" and p.company = '{0}' ".format(company))
	
	
	if filters.get("employee_group"):
		eg = filters.get("employee_group")
		condition+=("and p.employee_group = '{0}' ".format(eg))
	
	if filters.get("primary_consultant"):
		pc = filters.get("primary_consultant")
		condition+=("and p.primary_consultant= '{0}' ".format(pc))
	
	if filters.get("project"):
		pj = filters.get("project")
		condition+=("and p.name = '{0}' ".format(pj))
	
	return condition


def columns_rep():
	columns=[
		
		{
			"label": "Project",
			"fieldname": ("project"),
			"fieldtype": "Link",
			"options":"Project",
			"width": 200

		},
		{
			"label": "Project Name",
			"fieldname": ("project_name"),
			"fieldtype": "Data",
			"width": 200

		},
		
		{
			"fieldname": ("completion"),
			"label": "Completion %",
			"fieldtype": "Percent",
			"width": 200

		},
		{
			"fieldname": ("status"),
			"label": "Status",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": ("employee_group"),
			"label": "Employee Group",
			"fieldtype": "Link",
			"options":"Employee Group",
			"width": 200

		},
		{
			"fieldname": ("department"),
			"label": "Department",
			"fieldtype": "Data",
			"width": 200

		},
		{
			"fieldname": ("project_lead"),
			"label": "Project Lead",
			"fieldtype": "Link",
			"options":"Employee",
			"width": 200

		},
		{
			"fieldname": ("project_lead_name"),
			"label": "Project Lead Name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": ("total_cost"),
			"label": "Timesheet Cost",
			"fieldtype": "Currency",
			"width": 200

		},
		{
			"fieldname": ("total_expense"),
			"label": " Expense Claim Amount",
			"fieldtype": "Currency",
			"width": 200

		},
		{
			"fieldname": ("total_billable"),
			"label": "Billable Timesheet",
			"fieldtype": "Currency",
			"width": 200

		},
		{
			"fieldname": ("total_billed"),
			"label": "Sales Invoice Amount",
			"fieldtype": "Currency",
			"width": 200

		},
		{
			"fieldname": ("tax_amount"),
			"label": "Tax Amount",
			"fieldtype": "Currency",
			"width": 200

		},
		{
			"fieldname": ("total_purchase_invoice"),
			"label": "Purchase Invoice Amount",
			"fieldtype": "Currency",
			"width": 200

		},
		{
			"fieldname": ("expected_end_date"),
			"label": "Expected End Date",
			"fieldtype": "Date",
			"width": 200

		},
		{
			"fieldname": ("task_completion_percentage"),
			"label": "Task Completion %",
			"fieldtype": "Percent",
			"width": 200

		},
		{
			"fieldname": ("issue_completion_percentage"),
			"label": "Issue Completion %",
			"fieldtype": "Percent",
			"width": 200

		},
		{
			"fieldname": ("profit"),
			"label": "Profit",
			"fieldtype": "Currency",
			"width": 200

		},
		{
			"fieldname": ("profit_m"),
			"label": "Profit Margin %",
			"fieldtype": "Percent",
			"width": 200

		},

		{
			"fieldname": ("profit_p"),
			"label": "Profit %",
			"fieldtype": "Percent",
			"width": 200

		},
		{
			"fieldname": ("outstanding_amount"),
			"label": "Outstanding Amount",
			"fieldtype": "Currency",
			"width": 200

		},
		{
			"fieldname": ("outstanding_amount_p"),
			"label": "Outstanding Amount %",
			"fieldtype": "Percent",
			"width": 200

		},
		{
			"fieldname": ("paid_amount"),
			"label": "Payments Received",
			"fieldtype": "Currency",
			"width": 200

		},



		
	]
	return columns

def query(filters,condition):
	c_dict = {}
	d=[]
	data = frappe.db.sql("""
					select p.name,p.currency
					,p.project_name
					,p.percent_complete
					,p.status
					,p.employee_group
					,p.department
					,p.project_lead
					,p.project_lead_name
					,p.total_costing_amount
					,p.total_expense_claim
					,p.total_billable_amount
					,(select sum(si.base_grand_total) from `tabSales Invoice` si where si.project = p.name and si.docstatus = 1) as total_billed_amount,
					(select sum(si.base_total_taxes_and_charges) from `tabSales Invoice` si where si.project = p.name and si.docstatus = 1) as tax_amount
					,p.expected_end_date
					,p.total_purchase_cost
					,(select sum(si.outstanding_amount) from `tabSales Invoice` si where si.project = p.name and si.docstatus = 1) as sioa
					,(select sum(si.base_total) from `tabSales Invoice` si where si.project = p.name and si.docstatus = 1) as sigt
					,(select count(tk.name) from `tabTask` tk where tk.project = p.name) as tt_count
					,(select count(tk.name) from `tabIssue` tk where tk.project = p.name) as ti_count
					,(select count(tk.name) from `tabTask` tk where tk.project = p.name and tk.status = "Completed" ) as ct_count
					,(select count(ie.name) from `tabIssue` ie where ie.project = p.name and ie.status = "Closed" ) as ci_count
					from `tabProject` p
					join  `tabCompany` cp on cp.name = p.company
					where
					p.is_active = "Yes"
					{0}
	
	""".format(condition,filters.get("from_date")),filters,as_dict =1)
			
	for items in data:
		exchange_rate = 0.0
	
	
		default_currency=frappe.db.get_value("Company",filters.get("company"),"default_currency")
		si_currency = default_currency
		cp_currency = items.get("currency")
		if si_currency == cp_currency:
			exchange_rate=1
		else:
			exchange_rate = get_exchange_rate(si_currency,cp_currency)
			
		if items.get("tt_count")>0:
			tcp = (items.get("ct_count")/items.get("tt_count"))*100
		else:
			tcp = 0
		if items.get("ti_count"):
			icp = (items.get("ci_count")/items.get("ti_count"))*100
		else:
			icp = 0
		
		if items.get("total_billed_amount") :
			profit = (items.get("total_billed_amount") - items.get("total_purchase_cost") - items.get("total_expense_claim") - items.get("total_costing_amount"))
			# profit = profit * exchange_rate
		else :
			profit = 0
		if items.get("total_billed_amount")  and items.get("total_costing_amount") + items.get("total_purchase_cost") + items.get("total_expense_claim") > 0:
			profit_p = (((items.get("total_billed_amount") - items.get("total_purchase_cost") - items.get("total_expense_claim") - items.get("total_costing_amount")))/(items.get("total_costing_amount")+ items.get("total_purchase_cost") + items.get("total_expense_claim")))*100
		else:
			profit_p = 0

		if items.get("total_billed_amount"):
			oap = (items.get("sioa") *  flt(exchange_rate)/items.get("total_billed_amount"))*100
		else:
			oap = 0

		if items.get("total_billed_amount"):
			pm = (profit/items.get("total_billed_amount"))*100
		else :
			pm = 0

		
		query_data=frappe.db.sql("""select name from `tabSales Invoice` where project='{0}' and docstatus=1""".format(items.get("name")),as_dict=1)
		payment_amount=[]
		if len(query_data)>1:
			sales_name=list(map(lambda x:x.get("name"),query_data))
			payment_amount=frappe.db.sql("""select sum(pr.allocated_amount) as paid_amount from `tabPayment Entry Reference` as pr where pr.reference_name in {0} and pr.docstatus=1 """.format(tuple(sales_name)),as_dict=1)
		if len(query_data)==1:
			payment_amount=frappe.db.sql("""select sum(pr.allocated_amount) as paid_amount from  `tabPayment Entry Reference` as pr where pr.reference_name ='{0}' and pr.docstatus=1""".format(query_data[0].get("name")),as_dict=1)


		c_dict = frappe._dict({
			'project': items.get("name") if items.get("name") else None,
			'project_name':items.get("project_name"),
			'completion':items.get("percent_complete"),
			'status':items.get("status"),
			'employee_group':items.get("employee_group"),
			'department':items.get("department"),
			'project_lead':items.get("project_lead"),
			'project_lead_name':items.get("project_lead_name"),
			'total_cost':items.get("total_costing_amount") ,
			'total_expense':items.get("total_expense_claim") ,
			'total_billable':items.get("total_billable_amount"),
			'total_billed':items.get("total_billed_amount"),
			'total_purchase_invoice':items.get("total_purchase_cost"),
			'expected_end_date':items.get("expected_end_date"),
			'task_completion_percentage': tcp,
			'issue_completion_percentage':icp,
			'profit':profit,
			'profit_p':profit_p,
			'profit_m':pm,
			'outstanding_amount':flt(items.get("sioa")) * flt(exchange_rate) if exchange_rate > 0.0 else items.get("sioa"),
			'outstanding_amount_p':oap,
			'paid_amount': payment_amount[0].get("paid_amount") if payment_amount else 0

		})
	
		d.append(c_dict)

	
	return d


def get_chart_data(data):

	value3 = []
	value = []
	value2 = []
	labels = []
		
	for q in data:
		labels.append(q.get("project"))
		value.append(q.get("profit_m"))
		value2.append(q.get("completion"))
		value3.append(q.get("outstanding_amount_p"))

	
	datasets1 = []
	if value:
		datasets1.append({'name': ('Project Profit Margin %'), 'values': value})

	if value2:
		datasets1.append({'name': ('Project Completion %'), 'values': value2})	

	if value3:
		datasets1.append({'name': ('Project Outstanding Amount %'), 'values': value3})
	
	

	chart1 = {
		"data": {
			'labels': labels,
			'datasets': datasets1
		},
	}
	chart1["type"] = "line"

	
	return chart1

