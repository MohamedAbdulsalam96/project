# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "nextproject"
app_title = "Nextproject"
app_publisher = "Dexciss"
app_description = "nextproject"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "nextproject@dexciss.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/nextproject/css/nextproject.css"
# app_include_js = "/assets/nextproject/js/nextproject.js"

# include js, css files in header of web template
# web_include_css = "/assets/nextproject/css/nextproject.css"
# web_include_js = "/assets/nextproject/js/nextproject.js"
fixtures = [
		{"dt":"Custom Field", "filters": [["name", "in",("Timesheet-approved","Timesheet Detail-sales_order",
                "Timesheet Detail-approved","Employee-employee_costing_rate","Employee Group-group_lead","Employee Group-department","Employee Group-column_break_3",
                "Employee Group-group_lead_name","Employee Group-hod","Issue-test_session","Issue-task","Issue-base_estimated_cost","Issue-currency","Issue-estimated_cost",
                "Issue-department_","Issue-section_break_45","Issue-doctype_name","Issue-screenshot","Issue-console_log_description","Issue-if_issue_type_customisation_request_cr",
                "Issue-step_to_reproduce","Issue-task_created","Issue-estimated_cost_in_words","Issue-print_settings","Issue-heading","Issue-resolution_required",
                "Issue-section_break_16","Issue-employee_group","Issue-primary_consultant","Issue-project_lead","Issue-primary_consultant_name","Issue-project_lead_name",
                "Issue-column_break_20","Issue-grand_total","Issue-grand__total_cost_in_words","Issue-billing_section","Issue-column_break_17",
                "Project-currency","Project-auto_submit_invoice","Project-custom_last_projection_date",
                "Project-billing_based_on","Project-start_date","Project-total_project_value_excluding_taxes","Project-billing_frequency","Project-milestone_section",
                "Project-milestone","Project-auto_creation_doctype","Project-auto_submit_order","Project-recurring_charges","Project-recurring_item","Project-timesheet_item",
                "Project-timesheet_days","Project-billing_charges_based_on_activity_cost","Project-billing_charges_based_on_project_timesheet_charges","Project-team_details",
                "Project-employee_group","Project-project_lead","Project-project_lead_name","Project-column_break_25","Project-primary_consultant","Project-primary_consultant_name",
                "Project-sales_taxes_charges_template","Project-terms","Project-project_billing_rate","Project-sales_order_naming_series","Project-sales_invoice_naming_series",
                "Project-cr_last_billing_date","Project-cr_item","Project-price_list","Project-last_billing_date","Project-allocation_item",
                "Sales Order-project_allocation_bill","Sales Invoice-project_allocation_bill","Issue-sales_invoice","Issue-sales_order","Issue-completed_on","Task-ticket","Sales Invoice-ticket",
				"Appointment-custom_referral_code","Appointment-custom_sales_partner_name","Project-custom_uom","Project-custom_minimum_billing_hours",
				"Quotation-custom_commission","Quotation-custom_sales_partner","Quotation-custom_column_break_dkcbn","Quotation-custom_amount_eligible_for_commission","Quotation-custom_commission_rate","Quotation-custom_total_commission",
                'Task-custom_testing_details','Task-custom_tester','Task-custom_tester_name','Task-custom_testing_environment','Task-custom_column_break_t4abt','Task-custom_column_break_pirbn',
                'Task-custom_github_repository','Task-custom_branch','Task-custom_pr_branch','Task-custom_session_type','Task-custom_session_type','Task-custom_task_commit_items','Task-custom_ignore_testing',
                'Task-custom_column_break_faad9','Task-custom_test_case','Task-custom_test_case__project','Task-custom_test_case__task','Task-custom_section_break_j2t6k','Task-custom_inprogress','Employee-custom_probation_end_date',
                'Task-custom_end_date_changed_count','Task-custom_previous_exp_date','Project-custom_to_be_billed_in_advance','Activity Cost-custom_currency',"Activity Type-custom_currency"),]]}

    ]
# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"projects" : "public/js/projects.js"}

# include js in doctype views
doctype_js = {
	"Project" : "public/js/project.js",
    "Expense Claim Type":"public/js/custom_expense_claim_type.js",
	
	"Timesheet": "public/js/timesheet.js",
	# "Quotation": "public/js/custom_quotation.js",
	"Sales Order": "public/js/sales_order.js",
	"Issue":"public/js/issue.js",
	"Task":"public/js/task.js",
	"HD Ticket":"public/js/ticket.js",
	"Sales Invoice":"public/js/custom_sales_invoice.js",
    "Sales Partner" : "public/js/custom_sales_partner.js",
    "Appointment" : "public/js/custom_appointments.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "nextproject.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "nextproject.install.before_install"
# after_install = "nextproject.nextproject.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "nextproject.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Timesheet": {
		# "before_save":"nextproject.nextproject.custom.timesheet.get_activity_cost2",
		"validate":"nextproject.nextproject.custom.timesheet.validate_timesheet",
		"before_insert":"nextproject.nextproject.custom.timesheet.set_currency",
        "on_submit":"nextproject.nextproject.custom.timesheet.progress",
		# "on_submit":"nextproject.nextproject.custom.timesheet.timesheet_alert",
		"before_save":["nextproject.nextproject.custom.timesheet.validate_project",
        "nextproject.nextproject.custom.timesheet.get_activity_cost2"],
        "before_cancel":"nextproject.nextproject.custom.timesheet.timesheet_cancel",
	},

	"Job Offer": {
		"before_save":"nextproject.nextproject.job_offer_custom.employee_find",

	},

	"Sales Partner": {
        "validate" : "nextproject.nextproject.custom_sales_partner.validate"
	},
   
	"Task":{
		"before_save":["nextproject.task.validate_issue","nextproject.task.before_status"],
		"validate":["nextproject.task.get_days_and_hours","nextproject.task.budget_hours_validatation","nextproject.task.end_date_validate"],
        "after_save":"nextproject.task.status",
	},

	"Sales Invoice":{
		"before_cancel": "nextproject.nextproject.custom_sales_invoice.on_cancel_sales_invoice",
        "on_submit":"nextproject.nextproject.custom_sales_invoice.check_expense",
        "on_cancel":"nextproject.nextproject.custom_sales_invoice.cancel_expense",
        "before_submit": "nextproject.nextproject.custom_sales_invoice.before_cancel",
	},
	
	"Shift Type":{
		"validate":"nextproject.custom_shift_type.get_break_details"},
		
	"Issue":{
		"before_save":"nextproject.nextproject.custom_issue.get_price",
		"validate":"nextproject.nextproject.custom_issue.currency_update"
		
	},
	"Sales Order":{
		"before_cancel": "nextproject.nextproject.custom_sales_order.on_cancel_sales_order"

	},
    # "Sales Invoice": {
	# 	"after_insert":"nextproject.abc.set_last_sales_invoice",
	# 	"validate" : "nextproject.abc.new_name",
	# 	"on_submit" : "nextproject.abc.new_on_submit"
	# },
	"Project":{
		"before_save":"nextproject.nextproject.project.proj_active"
	},
    "Activity Cost":{
    	"before_save":"nextproject.event_activity_cost.set_cost"
	}

	
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"nextproject.tasks.all"
# 	],
	"daily": [
		"nextproject.custom_probation.check_probation_end_date",
		"nextproject.task.daily",
		"nextproject.task.daily_method",
		"nextproject.task.allocation_based_billing",
        "nextproject.nextproject.custom.timesheet.timesheet_alert",
        "nextproject.nextproject.custom.timesheet.set_status",
        # "nextproject.nextproject.doctype.pip_threshold.pip_threshold.threshold_crone_job",
		"nextproject.nextproject.doctype.project_revenue_projection.project_revenue_projection.revenue_cron_job"
	],
    
	"daily_long": [
        "nextproject.nextproject.doctype.pip_threshold.pip_threshold.pip_enqueue_cron_job",
        
	]
# 	"hourly": [
# 		"nextproject.tasks.hourly"
# 	],
# 	"weekly": [
# 		"nextproject.tasks.weekly"
# 	]
# 	"monthly": [
# 		"nextproject.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "nextproject.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
	# "erpnext.project.doctype.timesheet.timesheet.get_activity_cost": "nextproject.task.get_activity_cost"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Sales Order": "nextproject.nextproject.custom_sales_order_dashboard.get_data",
	"Project": "nextproject.nextproject.custom_project_dashboard.get_data",
	"Task": "nextproject.nextproject.custom_task_dashboard.get_data",
	"Sales Invoice":"nextproject.nextproject.custom_sales_invoice_dashboard.get_data",
    "HD Ticket":"nextproject.custom_hd_ticket_dashboard.get_data"
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]
auto_cancel_exempted_doctypes = [
	"Daily Scrum",
]
override_doctype_class = {
	'Sales Invoice': 'nextproject.custom_sales_invoice.CustomSalesInvoice',
    'Project':'nextproject.nextproject.project.CustomProject'
}
required_apps=["helpdesk"]


