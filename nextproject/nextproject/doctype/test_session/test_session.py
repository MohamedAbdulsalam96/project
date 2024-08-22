# Copyright (c) 2021, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import format_duration, today, get_fullname
from datetime import datetime, timedelta
from frappe.model.document import Document
from frappe.utils.data import escape_html
import requests


class TestSession(Document):
	def before_save(self):
		if self.test_cases:
			for test_case in self.test_cases:
				if not self.test_case_result:
					self.append("test_case_result",{
					'test_case':test_case.test_case,
					'steps_followed':test_case.steps_followed,
					'expected_result':test_case.expected_result
					})
				test_case_result = [test.test_case for test in self.test_case_result]
				if test_case.test_case not in test_case_result:
					self.append("test_case_result",{
					'test_case':test_case.test_case,
					'steps_followed':test_case.steps_followed,
					'expected_result':test_case.expected_result
					})
		
	def on_submit(self):
		current_time = None
		add_hours = None
		current_user = frappe.session.user
		employee_id = frappe.get_value("Employee", {"user_id": current_user}, ["name"])
		if self.overall_status == "PASS":
			frappe.db.set_value("Task",self.task,"status","Completed")
			frappe.db.set_value("Task",self.task,"custom_inprogress",False)
			timesheet_obj = frappe.new_doc("Timesheet")
			timesheet_obj.project = self.project
			timesheet_obj.company = self.company
			timesheet_obj.employee = employee_id
			for test_case in self.test_cases:
				if not current_time:
					current_time = datetime.now()
					add_hours = int(format_duration(test_case.estimated_work, hide_days=True)[:-1])
				else:
					current_time = current_time + timedelta(hours = add_hours)
					add_hours = int(format_duration(test_case.estimated_work, hide_days=True)[:-1])
				formatted_start_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
				duration_str = format_duration(test_case.estimated_work, hide_days=True)
				try:
					hours = int(duration_str[:-1])
				except ValueError:
					print(f"Error: Unable to convert {duration_str} to hours.")
					continue
				duration_timedelta = timedelta(hours=hours)
				timesheet_obj.append("time_logs",{"from_date":today(),"task":self.task,"completed": 1,"description":test_case.subject,"project":self.project,"from_time":formatted_start_time,
									"expected_hours":duration_timedelta.total_seconds() / 3600,
									"hours":duration_timedelta.total_seconds() / 3600})
			timesheet_obj.insert(ignore_permissions=True)
		else:
			frappe.db.set_value("Task",self.task,"status","Working")
			frappe.db.set_value("Task",self.task,"custom_inprogress",False)
			timesheet_obj = frappe.new_doc("Timesheet")
			timesheet_obj.project = self.project
			timesheet_obj.company = self.company
			timesheet_obj.employee = employee_id
			for test_case in self.test_cases:
				if not current_time:
					current_time = datetime.now()
					add_hours = int(format_duration(test_case.estimated_work, hide_days=True)[:-1])
				else:
					current_time = current_time + timedelta(hours = add_hours)
					add_hours = int(format_duration(test_case.estimated_work, hide_days=True)[:-1])
				formatted_start_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
				duration_str = format_duration(test_case.estimated_work, hide_days=True)
				try:
					hours = int(duration_str[:-1])
				except ValueError:
					print(f"Error: Unable to convert {duration_str} to hours.")
					continue
				duration_timedelta = timedelta(hours=hours)
				timesheet_obj.append("time_logs",{"from_date":today(),"task":self.task,"completed": 1,"description":test_case.subject,"project":self.project,"from_time":formatted_start_time,
									"expected_hours":duration_timedelta.total_seconds() / 3600,
									"hours":duration_timedelta.total_seconds() / 3600})
			timesheet_obj.insert(ignore_permissions=True)

	@frappe.whitelist()
	def git_release(self):
		git_setting = frappe.get_doc("Github Settings")

		username = git_setting.username
		repo = self.product

		"""POST API for release and tag"""
		token = git_setting.password

		url = f'https://api.github.com/repos/{username}/{repo}/releases'
		headers = {
			'Authorization': f'Bearer'+' '+token,
			'Content-Type': 'application/json',
		}
		data = {
			'tag_name': self.product_version,
			'target_commitish': 'main',
			'name': self.release_title,
			'body': self.release_description
		}

		response = requests.post(url, headers=headers, json=data)

		if response.status_code == 201:
			frappe.db.set_value("Test Session",self.name,'git_released',True)
			frappe.msgprint("Git Releases Successfully")
		else:
			frappe.throw(f"Failed to create release. Status code: {response.status_code}")
		
		returnTrue 
		
	def before_submit(self):
		for i in self.test_cases:
			if not i.status:
				frappe.throw("<b>Row {0}</b>:- Please Select Test Case {1} Result. It Always <b>Pass</b> Or <b>Fail</b>".format(i.idx,i.test_case))

		for j in self.test_case_result:
			if (not j.actual_result and not j.remark) or not j.actual_result or not j.remark:
				frappe.throw("<b>Row {0}</b>:- Please Enter Test Case {1} <b>Actual Result</b> and <b>Remark</b>".format(j.idx,j.test_case))

		if self.test_cases:
			oas_status = [status.status for status in self.test_cases]
			if 'FAIL' in oas_status:
				self.overall_status = "FAIL"
			else:
				self.overall_status = "PASS"

	@frappe.whitelist()			
	def create_pull_request(self):
		value = frappe.get_doc("Github Settings")
		token = value.password
		owner = value.username
		repo = self.product
		base_branch = self.base_branch
		head_branch = self.head_branch

		url = f'https://api.github.com/repos/{owner}/{repo}/pulls'

		headers = {
			'Authorization': f'Bearer'+' '+token,
			'Content-Type': 'application/json',
		}
		data = {
			'title': self.pull_request_title,
			'body': self.description,
			'base': base_branch,
			'head': head_branch
			}
		response = requests.post(url, headers=headers, json=data)

		if response.status_code == 201:
			pull_request_info = response.json()
			frappe.db.set_value("Test Session",self.name,'pull_request',True)
			pull_request_log = frappe.new_doc("Pull Request Log")
			pull_request_log.product = self.product
			pull_request_log.base_branch = self.base_branch
			pull_request_log.head_branch = self.head_branch
			pull_request_log.pull_request_no= pull_request_info['number']
			pull_request_log.pull_request_title = self.pull_request_title
			pull_request_log.reference_name = self.name
			pull_request_log.state = {pull_request_info['state']}
			pull_request_log.description = self.description 
			pull_request_log.insert()
			frappe.msgprint(f"Pull Request #{pull_request_info['number']} created successfully.")
		else:
			frappe.msgprint(f"Failed to Create Pull Request: {response.status_code}")

		return True