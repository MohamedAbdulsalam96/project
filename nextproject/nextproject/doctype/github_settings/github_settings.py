# Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GithubSettings(Document):
	@frappe.whitelist()
	def update_latest_code(self,repo_list):
		if repo_list:
			cur_repo = []
			all_product = frappe.db.get_list('GitHub Repository', pluck='name')
			for repo in repo_list:
				if repo["repo"] not in all_product:
					if repo["repo"] not in cur_repo:
						cur_repo.append(repo["repo"])
						new_product = frappe.new_doc("GitHub Repository")
						new_product.product_name = repo["repo"]
						new_product.github_repo_url = repo["url"]
						new_product.insert()
			frappe.msgprint("Successfully Updated...")