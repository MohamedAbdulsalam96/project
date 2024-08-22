# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta
from frappe.utils import (add_days,add_months,flt,getdate,today)
from erpnext.setup.utils import get_exchange_rate

class ProjectRevenueProjection(Document):
	def before_save(self):
		total_billing_amount,total_costing_amount = 0,0	
		for consultant in self.consultant_details:
			total_billing_amount += consultant.bill_amount
			total_costing_amount += consultant.cost_amount
		self.projected_amount = total_billing_amount
		self.projected_costing_amount = total_costing_amount

		project_cur,comp = frappe.get_cached_value("Project", self.project, ["currency","company"])
		company_cur = frappe.get_cached_value("Company", comp, 'default_currency')

		if project_cur == company_cur:
			self.base_projected_billing_amount = self.projected_amount
			self.base_projected_costing_amount = self.projected_costing_amount
		else:
			exc_rate = get_exchange_rate(project_cur, company_cur)
			self.conversion_rate = exc_rate
			self.project_currency = project_cur
			self.base_projected_billing_amount = self.projected_amount * exc_rate
			self.base_projected_costing_amount = self.projected_costing_amount * exc_rate

		sales_invoice = frappe.get_all('Sales Invoice', filters={
        'project': self.project,
        'docstatus': 1,
        'posting_date': ['between', [self.last_billing_date, self.next_billing_date]]
		}, fields=['*'],
		limit=1)

		print(" sales_invoice : " ,sales_invoice)

		base_amt = 0

		if sales_invoice:
			self.sales_invoice = sales_invoice[0].name
			item = frappe.get_all(
				'Sales Invoice Item',
				filters={'parent': sales_invoice[0].name},
				fields=['base_amount'],
				limit=1
			)			
			if item:
				base_amt = item[0].base_amount
				self.invoiced_amount = base_amt

		if base_amt < self.projected_amount and  base_amt > 0:
			self.status = 'Partially Billed'
		elif base_amt > self.projected_amount:
			self.status = 'Closed'
		elif base_amt == 0:
			self.status = 'Open'


def create_rev_for_fixed_recurring(data):
	for consultant_id, consultant_info in data['consultant_data'].items():
		# Check if a project record with the same last and next billing date already exists
		existing_projection = frappe.db.get_value('Project Revenue Projection', {
			'project': data['project'],
			'last_billing_date': data['projects_last_billing_date'],
			'next_billing_date': data['projects_next_billing_date'],
		}, 'name')

		if existing_projection:
			print("*****EXISTING PROJECTION FOUND FOR RECUR*******",existing_projection)
			return
		else:
			# Create a new record for the project if none exists with the same billing dates
			doc = frappe.new_doc('Project Revenue Projection')
			doc.project = data['project']
			doc.billing_based_on = data['billing_based_on']
			doc.last_billing_date = data['projects_last_billing_date']
			doc.next_billing_date = data['projects_next_billing_date']

			for consultant_id, consultant_info in data['consultant_data'].items():
				doc.append('consultant_details', {
					'primary_consultant': consultant_info['primary_consultant_name'],
					'billing_rate': consultant_info['billing_rate'],
					'costing_rate': consultant_info['costing_rate'],
					'expected_time_in_hours': consultant_info['expected_time_in_hours'],
					'bill_amount': consultant_info['projected_amount'],
					'cost_amount': consultant_info['projected_amount'],
				})

			# Save the document after appending all consultants
			doc.insert(ignore_permissions=True)
			doc.save()
			print(f"Revenue projection created for project {data['project']} with all consultant details added.")


def create_revenue_projection(data):
	# Iterate over consultants
	print("data coming here  : ",data)
	for consultant_id, consultant_info in data['consultant_data'].items():
		# Check if a project record with the same last and next billing date already exists
		existing_projection = frappe.db.get_value('Project Revenue Projection', {
			'project': data['project'],
			'last_billing_date': data['projects_last_billing_date'],
			'next_billing_date': data['projects_next_billing_date']
		}, 'name')

		if existing_projection:
			print("*****EXISTING PROJECTION FOUND FOR 88*******")
			return
		else:
			# Create a new record for the project if none exists with the same billing dates
			doc = frappe.new_doc('Project Revenue Projection')
			doc.project = data['project']
			doc.billing_based_on = data['billing_based_on']
			doc.last_billing_date = data['projects_last_billing_date']
			doc.next_billing_date = data['projects_next_billing_date']

			for consultant_id, consultant_info in data['consultant_data'].items():
				# for task in consultant_info['tasks']:
				overlap_hours = consultant_info.get('total_hours_spent') or consultant_info.get('expected_time_in_hours') or 0
				first_task = consultant_info['tasks'][0]

				doc.append('consultant_details', {
					'primary_consultant': consultant_info['primary_consultant_name'],
					'billing_rate': consultant_info['billing_rate'],
					'costing_rate': consultant_info['costing_rate'],
					'bill_amount': consultant_info['projected_billing_amount'],
					'cost_amount': consultant_info['projected_costing_amount'],
					'task': first_task['task_name'],
					'hours': overlap_hours,
				})

			# Save the document after appending all consultants
			doc.insert(ignore_permissions=True)
			doc.save()
			print(f"Revenue projection created for project {data['project']} with all consultant details added.")


@frappe.whitelist(allow_guest=True)  
def revenue_cron_job():
	filters = {
		'status': 'Open',
		'billing_based_on': ['in', ['Timesheet Based', 'Milestone Based', 'Fixed Recurring', 'Allocation Based']],
		# 'custom_last_projection_date': ['<', today()] 
	}

	projects = frappe.get_all("Project", filters, ["*"])
	for project in projects:

		if project.billing_based_on == 'Allocation Based':
			dates = Allocation_Based(project)

			if dates and dates[0] is not None and dates[1] is not None:
				last_billing, next_billing = dates[0].strftime("%Y-%m-%d"), dates[1].strftime("%Y-%m-%d")

				frappe.db.set_value("Project", project.name, "custom_last_projection_date", next_billing)

				project_and_consultant_data = {
					'project': project.name,
					'billing_based_on': project.billing_based_on,
					'consultant_data': {},
					'projects_last_billing_date': last_billing,
					'projects_next_billing_date': next_billing
				}

				query = """
					SELECT 
						name, 
						exp_start_date, 
						exp_end_date, 
						status 
					FROM 
						`tabTask` 
					WHERE 
						project = %s 
						AND is_billable = 1 
						AND fixed_cost_based_billing = 0 
						AND status IN ('Open', 'Pending Review', 'Overdue', 'Working', 'New')
						AND exp_start_date IS NOT NULL
						AND exp_end_date IS NOT NULL
						AND expected_time > 0
						AND exp_start_date <= %s
						AND exp_end_date >= %s;
				"""
				al_tasks = frappe.db.sql(query, (project.name, last_billing, next_billing), as_dict=True)
				consultant_data = project_and_consultant_data['consultant_data']

				if al_tasks:
					for task in al_tasks:
						consultant_info = billing_rates_for_timesheet_and_allocation(task, project.project_name, last_billing, next_billing)						
						if consultant_info and consultant_info.get('primary_consultant_name'):
							consultant_name = consultant_info['primary_consultant_name']							
							if consultant_name in consultant_data:
								consultant_data[consultant_name]['expected_time_in_hours'] += consultant_info['total_hours_spent']
								consultant_data[consultant_name]['tasks'].append(consultant_info['tasks'][0])
							else:
								consultant_data[consultant_name] = consultant_info

					for consultant_name, consultant_info in consultant_data.items():
						expected_time_in_hours = consultant_info['total_hours_spent']
						billing_rate = consultant_info['billing_rate']
						costing_rate = consultant_info['costing_rate']

						amounts = billing_calculator(
							billing_rate=billing_rate,
							costing_rate=costing_rate,
							expected_time_in_hours=expected_time_in_hours
						)
						
						consultant_data[consultant_name]['projected_billing_amount'] = amounts[0]
						consultant_data[consultant_name]['projected_costing_amount'] = amounts[1]
						consultant_data[consultant_name]['expected_time_in_hours'] = expected_time_in_hours

			create_revenue_projection(project_and_consultant_data)

	# FIXED RECURRING CONDITION 
		elif project.billing_based_on in ['Fixed Recurring']:
			dates = Fix_Recur_Timesheet_Based(project)

			if dates and dates[0] is not None and dates[1] is not None:
				last_billing , next_billing = dates[0].strftime("%Y-%m-%d"),dates[1].strftime("%Y-%m-%d")
				
				frappe.db.set_value("Project", project.name, "custom_last_projection_date", next_billing)

				project_and_consultant_data = {
				'project': project.name,
				'billing_based_on': project.billing_based_on,
				'consultant_data': {},
				'projects_last_billing_date': last_billing,
				'projects_next_billing_date': next_billing
				}

				if project.primary_consultant:
					query = """
						SELECT act.billing_rate, act.costing_rate
						FROM `tabActivity Cost` as act
						WHERE act.employee = %s AND act.activity_type = %s
					"""
					rates = frappe.db.sql(query, (project.primary_consultant, project.project_name), as_dict=True)
					
					if rates:
						billing_rate = rates[0].get('billing_rate')
						costing_rate = rates[0].get('costing_rate')
					else:
						billing_rate = 0
						costing_rate = 0

					it_price_rate = frappe.get_value('Project',project.name , 'recurring_charges')
					if it_price_rate is None:
						recurring_item = frappe.get_value('Project',project.name , 'recurring_item')
						it_price_rate = frappe.get_value('Item Price', {'item_code': recurring_item}, 'price_list_rate')
						if not it_price_rate:
							frappe.log_error(f"Recurring charges not found for project {project.name}")

					data = {
						'primary_consultant_name': project.primary_consultant,
						'billing_rate': billing_rate,
						'costing_rate': costing_rate,
						'projected_amount': it_price_rate,
						'expected_time_in_hours': 0,
						'projected_billing_amount' : 0,
						'projected_costing_amount' : 0
					}
					
					project_and_consultant_data['consultant_data'][project.primary_consultant] = data
					create_rev_for_fixed_recurring(project_and_consultant_data)


	# #  TIMESHEET BASED CONDITION**********************************************DONE***********************************
		
		elif project.billing_based_on == 'Timesheet Based':
			dates = Fix_Recur_Timesheet_Based(project)

			if dates and dates[0] is not None and dates[1] is not None:
				last_billing , next_billing = dates[0].strftime("%Y-%m-%d"),dates[1].strftime("%Y-%m-%d")

				frappe.db.set_value("Project", project.name, "custom_last_projection_date", next_billing)

				project_and_consultant_data = {
					'project': project.name,
					'billing_based_on': project.billing_based_on,
					'consultant_data': {},
					'projects_last_billing_date': last_billing,
					'projects_next_billing_date': next_billing
				}

				querry = """
					SELECT 
						name, 
						exp_start_date, 
						exp_end_date, 
						status 
					FROM 
						`tabTask` 
					WHERE 
						project = %s 
						AND is_billable = 1 
						AND fixed_cost_based_billing = 0 
						AND status IN ('Open', 'Pending Review', 'Overdue', 'Working', 'New')
						AND exp_start_date IS NOT NULL
						AND exp_end_date IS NOT NULL
						AND expected_time > 0
						AND exp_start_date <= %s
						AND exp_end_date >= %s;
					"""
				tm_tasks = frappe.db.sql(querry,(project.name,next_billing,last_billing),as_dict=True)
				consultant_data = project_and_consultant_data['consultant_data']

				if tm_tasks:
					for task in tm_tasks:
						consultant_info = billing_rates_for_timesheet_and_allocation(task,project.project_name,last_billing,next_billing)
						
						if consultant_info and consultant_info.get('primary_consultant_name'):
							consultant_name = consultant_info['primary_consultant_name']
							if consultant_name in consultant_data:
								if 'expected_time_in_hours' not in consultant_data[consultant_name]:
									consultant_data[consultant_name]['expected_time_in_hours'] = 0

								consultant_data[consultant_name]['expected_time_in_hours'] += consultant_info['total_hours_spent']
								consultant_data[consultant_name]['tasks'].append(consultant_info['tasks'][0])
							else:
								consultant_data[consultant_name] = consultant_info
						else:
							print(f"No billing rates found for task {task.get('name')}")

					for consultant_name, consultant_info in consultant_data.items():
						expected_time_in_hours = consultant_info['total_hours_spent']
						billing_rate = consultant_info['billing_rate']
						costing_rate = consultant_info['costing_rate']

						amounts = billing_calculator(
							billing_rate=billing_rate,
							costing_rate=costing_rate,
							expected_time_in_hours=expected_time_in_hours
						)
						
						consultant_data[consultant_name]['projected_billing_amount'] = amounts[0]
						consultant_data[consultant_name]['projected_costing_amount'] = amounts[1]
						consultant_data[consultant_name]['expected_time_in_hours'] = expected_time_in_hours

					create_revenue_projection(project_and_consultant_data)	

	# # MILESTONE BASED CONDITION*****************************************DONE****************************************************************************************

		elif project.billing_based_on == 'Milestone Based':
			print("******milestone****")
			dates = Milestone_Based(project)
			print("dats  : ",dates)
			if dates and dates[0] is not None and dates[1] is not None:
				last_projection_date , next_projection_billing_date = dates[0].strftime("%Y-%m-%d"),dates[1].strftime("%Y-%m-%d")
				print("******custom_last_projection_date****",dates[1])
				
				frappe.db.set_value("Project", project.name, "custom_last_projection_date", next_projection_billing_date)

				project_and_consultant_data = {
					'project': project.name,
					'billing_based_on': project.billing_based_on,
					'consultant_data': {},
					'projects_last_billing_date': last_projection_date,
					'projects_next_billing_date': next_projection_billing_date
				}

				if last_projection_date or not next_projection_billing_date:
					querry = """
							SELECT 
							name, 
							exp_end_date, 
							status ,
							expected_time,
							exp_start_date
							FROM 
								`tabTask` 
							WHERE 
								project = %s 
								AND status IN ('Open', 'Pending Review', 'Overdue', 'Working', 'New')
								AND exp_start_date IS NOT NULL
								AND exp_end_date IS NOT NULL
								AND expected_time > 0
								AND exp_end_date BETWEEN %s AND %s;
							"""

					ml_tasks = frappe.db.sql(querry,(project.name,last_projection_date,next_projection_billing_date),as_dict=True)					
					print("****ml_task",ml_tasks)
					consultant_data = project_and_consultant_data['consultant_data']

					if ml_tasks:
						for task in ml_tasks:
							consultant_info = billing_rates(task,project.project_name,last_projection_date,next_projection_billing_date)
							if consultant_info and consultant_info.get('primary_consultant_name'):
								consultant_name = consultant_info['primary_consultant_name']
								if consultant_name in consultant_data:
									if 'expected_time_in_hours' not in consultant_data[consultant_name]:
										consultant_data[consultant_name]['expected_time_in_hours'] = 0
									consultant_data[consultant_name]['expected_time_in_hours'] += consultant_info['expected_time_in_hours']
									consultant_data[consultant_name]['tasks'].append(consultant_info['tasks'][0])
								else:
									consultant_data[consultant_name] = consultant_info
							else:
								print(f"No billing rates found for task {task.get('name')}")

						for consultant_name, consultant_info in consultant_data.items():
							expected_time_in_hours = consultant_info['expected_time_in_hours']
							billing_rate = consultant_info['billing_rate']
							costing_rate = consultant_info['costing_rate']

							amounts = billing_calculator(
								billing_rate=billing_rate,
								costing_rate=costing_rate,
								expected_time_in_hours=expected_time_in_hours
							)
							
							consultant_data[consultant_name]['projected_billing_amount'] = amounts[0]
							consultant_data[consultant_name]['projected_costing_amount'] = amounts[1]
							consultant_data[consultant_name]['overlap_hours'] = 0
						create_revenue_projection(project_and_consultant_data)


@frappe.whitelist(allow_guest=True)
def Allocation_Based(project):
	projection_period = int(frappe.db.get_value('Project Revenue Settings', None, 'projection_period'))
	next_billing_date = None
	if project.last_billing_date and projection_period:
		next_billing_date = project.last_billing_date + timedelta(days=projection_period)
	else:
		frappe.log_error("Unable to retrieve last billing date or projection period.")
	return [project.last_billing_date,next_billing_date]


@frappe.whitelist(allow_guest=True)
def Fix_Recur_Timesheet_Based(project):
	last_billing_date = frappe.db.get_value('Project', project, 'start_date')
	billing_frequency = frappe.db.get_value('Project', project, 'billing_frequency')
	next_billing_date = None

	if billing_frequency == 'Daily':
		next_billing_date = last_billing_date + timedelta(days=1)

	elif billing_frequency == 'Weekly':
		next_billing_date = last_billing_date + timedelta(weeks=1)

	elif billing_frequency == 'Monthly':
		next_billing_date = frappe.utils.add_months(last_billing_date, 1)

	elif billing_frequency == 'Quaterly':
		next_billing_date = frappe.utils.add_months(last_billing_date, 3)

	elif billing_frequency == 'Bi-Yearly':
		next_billing_date = frappe.utils.add_months(last_billing_date, 6)

	elif billing_frequency == 'Yearly':
		next_billing_date = frappe.utils.add_months(last_billing_date, 12)

	elif billing_frequency == 'Custom':
		days_numbers_data = frappe.db.sql("""
			SELECT td.day_number
			FROM `tabTimesheet Days` td
			WHERE td.parent = %s
		""", (project.name,), as_dict=1)

		days_numbers = sorted([int(d['day_number']) for d in days_numbers_data])

		if days_numbers:
			for day in days_numbers:
				if day > last_billing_date.day:
					next_billing_date = datetime(last_billing_date.year, last_billing_date.month, day)
					break

			if not next_billing_date:
				next_month = last_billing_date.month + 1
				next_year = last_billing_date.year

				if next_month > 12:
					next_month = 1
					next_year += 1

				next_billing_date = datetime(next_year, next_month, days_numbers[0]).date()
		else:
			frappe.log_error(f"No day_number found for project {project}")

	return [last_billing_date,next_billing_date]


@frappe.whitelist(allow_guest=True)
def Milestone_Based(project):
	# print("**************",project)
	last_projection_date = getdate(today())
	next_projection_billing_date = None

	milestone_data = frappe.db.sql("""
			SELECT pmc.milestone
			FROM `tabProject Milestone Child` pmc
			WHERE pmc.parent = %s
			LIMIT 1
		""", (project.name,), as_dict=1)

	if milestone_data[0]:   
		task = frappe.db.get_value('Task', {
			'name': milestone_data[0]['milestone'],
			'exp_end_date': (">", last_projection_date)
		}, 'exp_end_date')
		
		if task:
			next_projection_billing_date = getdate(task)
	else:
		frappe.log_error(f"No valid milestone found in Project {project.name} with a future task's expected end date.")
	# print("**********Next pj ***********",next_projection_billing_date)
	return [last_projection_date, next_projection_billing_date]


# FUNCTION FOR CONSULTS COSTING AND BILLING RATES
@frappe.whitelist(allow_guest=True)
def billing_rates(task,project_actual_name,last_projection_date,next_projection_billing_date):
	primary_consultant_name = frappe.get_value('Task', task.name, 'primary_consultant')
	query = """
		SELECT act.billing_rate, act.costing_rate
		FROM `tabActivity Cost` as act
		WHERE act.employee = %s AND act.activity_type = %s
	"""
	rates = frappe.db.sql(query, (primary_consultant_name, project_actual_name), as_dict=True)
	if not rates: 
		return {}  
	if rates:
		billing_rate = rates[0].get('billing_rate')
		costing_rate = rates[0].get('costing_rate')
	else:
		billing_rate = 0
		costing_rate = 0

	expected_time_in_hours = frappe.get_value('Task', task.name, 'expected_time')
	total_duration_in_days = frappe.get_value('Task', task.name, 'total_duration_in_days')
	data = {
		'primary_consultant_name': primary_consultant_name,
		'billing_rate': billing_rate,
		'costing_rate': costing_rate,
		'tasks': [{
            'task_name': task.name,
			'task_status':task.status,
            'last_billing_date': last_projection_date,
            'next_billing_date': next_projection_billing_date
        }],
		'expected_time_in_hours': expected_time_in_hours,
		'total_duration_in_days': total_duration_in_days,
	}
	return data


@frappe.whitelist(allow_guest=True)
def billing_calculator(billing_rate, costing_rate, expected_time_in_hours):
    billing_amount = billing_rate * expected_time_in_hours
    costing_amount = costing_rate * expected_time_in_hours
    return [billing_amount,costing_amount]


@frappe.whitelist(allow_guest=True)
def get_holiday_list(start_date, end_date):
    holidays = frappe.get_all('Holiday', filters={
        'holiday_date': ['between', [start_date, end_date]]
    }, fields=['holiday_date'])
    return [holiday['holiday_date'] for holiday in holidays]


@frappe.whitelist(allow_guest=True)
def calculate_working_days(start_date, end_date, holidays):
	start = datetime.strptime(start_date, "%Y-%m-%d")
	end = datetime.strptime(end_date, "%Y-%m-%d")
	working_days = 0
	while start <= end:
		if start.weekday() < 5 and start.strftime("%Y-%m-%d") not in holidays: 
			working_days += 1
		start += timedelta(days=1)
	return working_days

@frappe.whitelist(allow_guest=True)
def adjust_hours_based_on_holidays(expected_time_in_hours, working_days):
    # Assuming 8 working hours per day
    return working_days * 8 if expected_time_in_hours > working_days * 8 else expected_time_in_hours


@frappe.whitelist(allow_guest=True)
def billing_rates_for_timesheet_and_allocation(task, project_name, last_billing, next_billing):
	primary_consultant_name = frappe.get_value('Task', task, 'primary_consultant')
	query = """
		SELECT act.billing_rate, act.costing_rate
		FROM `tabActivity Cost` as act
		WHERE act.employee = %s AND act.activity_type = %s
	"""
	rates = frappe.db.sql(query, (primary_consultant_name, project_name), as_dict=True)
	if not rates:
		return {}
	
	billing_rate = rates[0].get('billing_rate')
	costing_rate = rates[0].get('costing_rate')
	expected_start_date = frappe.get_value('Task', task, 'exp_start_date')
	expected_end_date = frappe.get_value('Task', task, 'exp_end_date')
	last_billing_date = last_billing
	next_billing_date = next_billing
	task_start_date =  datetime.strftime(expected_start_date,"%Y-%m-%d")
	task_end_date = datetime.strftime(expected_end_date,"%Y-%m-%d")

 
	# 1.if task start date is before last_billing_date and end date is before next_billing_date
	if task_start_date < last_billing_date and task_end_date < next_billing_date:
		# calcuate working days between these two dates  (last_billing_date and task_end_date)
		# then working days muliplied with the tasks duration_per_day_in_hours variable
		duration_per_day_in_hours = frappe.get_value('Task', task, 'duration_per_day_in_hours')
		total_duration_in_days = frappe.get_value('Task', task, 'total_duration_in_days')

		holidays = get_holiday_list(last_billing_date,task_end_date)
		working_days = calculate_working_days(last_billing_date, task_end_date, holidays)
		total_hours_spent = duration_per_day_in_hours * working_days
		data = {
		'primary_consultant_name': primary_consultant_name,
		'billing_rate': billing_rate,
		'costing_rate': costing_rate,
		'tasks': [{
            'task_name': task.name,
			'task_status':task.status,
            'last_billing_date': last_billing_date,
            'next_billing_date': next_billing_date
        }],
		'total_hours_spent': total_hours_spent,
		'total_duration_in_days': total_duration_in_days,
		}
		return data

	# 2.if task start date is after last_billing_date and end date is after next_billing_date
	elif task_start_date > last_billing_date and task_end_date > next_billing_date:
		duration_per_day_in_hours = frappe.get_value('Task', task, 'duration_per_day_in_hours')
		total_duration_in_days = frappe.get_value('Task', task, 'total_duration_in_days')

		holidays = get_holiday_list(task_start_date,next_billing_date)
		working_days = calculate_working_days(task_start_date, next_billing_date, holidays)
		total_hours_spent = duration_per_day_in_hours * working_days
		data = {
		'primary_consultant_name': primary_consultant_name,
		'billing_rate': billing_rate,
		'costing_rate': costing_rate,
		'tasks': [{
            'task_name': task.name,
			'task_status':task.status,
            'last_billing_date': last_billing_date,
            'next_billing_date': next_billing_date
        }],
		'total_hours_spent': total_hours_spent,
		'total_duration_in_days': total_duration_in_days,
		}
		return data

	# 3.if task start date is before last_billing_date and end date is after next_billing_date
	elif task_start_date < last_billing_date and task_end_date > next_billing_date:
		duration_per_day_in_hours = frappe.get_value('Task', task, 'duration_per_day_in_hours')
		total_duration_in_days = frappe.get_value('Task', task, 'total_duration_in_days')

		holidays = get_holiday_list(last_billing_date,next_billing_date)
		working_days = calculate_working_days(last_billing_date, next_billing_date, holidays)
		total_hours_spent = duration_per_day_in_hours * working_days
		data = {
		'primary_consultant_name': primary_consultant_name,
		'billing_rate': billing_rate,
		'costing_rate': costing_rate,
		'tasks' : [{
			'task_name': task.name,
			'task_status':task.status,
			'last_billing_date': last_billing_date,
			"next_billing_date": next_billing_date
		}],
		'total_hours_spent': total_hours_spent,
		'total_duration_in_days': total_duration_in_days,
		}
		return data

	# 4.if task start date and end date is in between last_billing_date and next_billing_date  
	elif task_start_date >= last_billing_date and task_end_date <= next_billing_date:
		expected_time_in_hours = frappe.get_value('Task', task, 'expected_time')
		total_duration_in_days = frappe.get_value('Task', task, 'total_duration_in_days')

		data = {
		'primary_consultant_name': primary_consultant_name,
		'billing_rate': billing_rate,
		'costing_rate': costing_rate,
		'tasks' : [{
			'task_name' : task.name,
			'task_status':task.status,
			'last_billing_date': last_billing_date,
			"next_billing_date": next_billing_date,
		}],
		'total_hours_spent': expected_time_in_hours,
		'total_duration_in_days': total_duration_in_days,
		}
		return data

