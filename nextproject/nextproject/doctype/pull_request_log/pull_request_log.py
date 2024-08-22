# Copyright (c) 2024, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests
 
class PullRequestLog(Document):
	@frappe.whitelist()
	def close_document(self):
		doc1 = frappe.get_doc("Github Settings")
		token = doc1.password
		owner = doc1.username
		repo = self.product
		pull_request_number = self.pull_request_no

		url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_request_number}'

		headers = {
			'Authorization': f'token {token}',
			'Accept': 'application/vnd.github.v3+json'
		}

		if self.state == "open":
			self.state = "Closed"
			data = {
				'state': 'close'
				}
		 
			response = requests.patch(url, headers=headers, json=data)

			if response.status_code == 200:
				frappe.msgprint(f"Pull Request #{pull_request_number} closed successfully.")
				frappe.db.set_value("Test Session",self.reference_name,'pull_request',False)
				self.save()
			else:
				error = frappe.new_doc ("Error Pull Request Log")
				error.reference_name = self.name
				error.reference_doctype = self.doctype
				error.method = "Close Pull Request Error"
				error.error = {response.text}
				error.save()
				frappe.msgprint(f"Failed to Close pull request: {response.status_code}")

		elif self.state == "Closed":
			self.state = "open"
			data = {'state': 'open'}

			response = requests.patch(url, headers=headers, json=data)

			if response.status_code == 200:
				frappe.msgprint(f"Pull Request #{pull_request_number} Open successfully.")
				frappe.db.set_value("Test Session",self.reference_name,'pull_request',True)
				self.save()
			else:
				error = frappe.new_doc ("Error Pull Request Log")
				error.reference_name = self.name
				error.reference_doctype = self.doctype
				error.method = "Open Pull Request Error"
				error.error = {response.text}
				error.save()
				frappe.msgprint(f"Failed to Open pull request: {response.status_code}")
		
	@frappe.whitelist()
	def merge_pull_request(self):
		doc1 = frappe.get_doc("Github Settings")
		token = doc1.password
		owner = doc1.username
		repo = self.product
		pull_number = self.pull_request_no

		if not self.merge_title:
			frappe.throw ("Merge Pull Request Title is mandatory")
		if not self.merge_description:
			frappe.throw (" Merge Pull Request Description is mandatory")

		url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/merge"

		headers = {
			"Authorization": f"token {token}",
			"Accept": "application/vnd.github.v3+json"
		}

		data = {
			"commit_title": self.merge_title,
			"commit_message": self.merge_description,
			"merge_method": "merge"
		}

		response = requests.put(url, headers=headers, json=data)

		if response.status_code == 200:
			self.state = 'Closed'
			self.merge_request_state = 'Merged'
			frappe.msgprint("Created Merge pull request")
		else:
			error = frappe.new_doc ("Error Pull Request Log")
			error.reference_name = self.name
			error.reference_doctype = self.doctype
			error.method = " Failed to Merge Pull Request Error"
			error.error = {response.text}
			error.save()
			frappe.msgprint(f"Failed to merge pull request. Status code: {response.status_code}")
		