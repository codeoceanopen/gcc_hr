app_name = "gcc_hr"
app_title = "GCC HR Compliance"
app_publisher = "GCC HR Compliance"
app_description = "GCC HR Localization and Compliance Platform for Frappe HR - Saudi Arabia, Qatar, UAE, Oman, Bahrain, Kuwait"
app_email = "code.ocean.open@gmail.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["erpnext", "hrms"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "gcc_hr",
		"logo": "/assets/frappe/images/frappe-framework-logo.svg",
		"title": "GCC HR Compliance",
		"route": "/gcc_hr",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gcc_hr/css/gcc_hr.css"
# app_include_js = "/assets/gcc_hr/js/gcc_hr.js"

# include js, css files in header of web template
# web_include_css = "/assets/gcc_hr/css/gcc_hr.css"
# web_include_js = "/assets/gcc_hr/js/gcc_hr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gcc_hr/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "gcc_hr/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website Route Rules
# --------------------
# Vue Router uses history mode (see frontend/src/router/index.js), so every
# sub-route under /gcc_hr needs to resolve server-side to the same SPA shell
# (www/gcc_hr.py) -- otherwise a direct link/refresh to e.g.
# /gcc_hr/settings/countries 404s instead of letting the client-side router
# handle it. Same pattern qcore uses for its own SPA.
website_route_rules = [
	{"from_route": "/gcc_hr/<path:app_path>", "to_route": "gcc_hr"},
	{"from_route": "/gcc_hr", "to_route": "gcc_hr"},
]

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "gcc_hr.utils.jinja_methods",
# 	"filters": "gcc_hr.utils.jinja_filters"
# }

# Installation
# ------------

after_install = "gcc_hr.install.after_install"

# Fixtures
# --------
# Static reference data (roles, custom fields, default notifications) that is
# re-synced on every `bench migrate`. User-editable settings (HR Country
# Settings, default expiry thresholds, default score bands) are seeded once,
# idempotently, via after_install instead -- see gcc_hr/install.py.

fixtures = [
	{
		"doctype": "Role",
		"filters": [
			[
				"name",
				"in",
				[
					"GCC HR Administrator",
					"HR Officer",
					"Payroll Manager",
					"Payroll Officer",
					"Compliance Manager",
					"Compliance Officer",
					"Government Integration Manager",
				],
			]
		],
	},
	{
		"doctype": "Custom Field",
		"filters": [["dt", "=", "Contract"], ["fieldname", "like", "gcc_%"]],
	},
	{
		"doctype": "Notification",
		"filters": [["name", "like", "GCC HR:%"]],
	},
]

# Uninstallation
# ------------

# before_uninstall = "gcc_hr.uninstall.before_uninstall"
# after_uninstall = "gcc_hr.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "gcc_hr.utils.before_app_install"
# after_app_install = "gcc_hr.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "gcc_hr.utils.before_app_uninstall"
# after_app_uninstall = "gcc_hr.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "gcc_hr.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gcc_hr.notifications.get_notification_config"

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
	"Employee": {
		"after_insert": "gcc_hr.gcc_hr_core.doctype.employee_compliance_profile.employee_compliance_profile.create_compliance_profile",
		"on_update": "gcc_hr.gcc_hr_core.doctype.employee_compliance_profile.employee_compliance_profile.sync_compliance_profile",
	},
	"Contract": {
		"validate": "gcc_hr.overrides.contract.compute_total_salary",
	},
	"GCC HR Company Settings": {
		"on_update": [
			"gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings.run_country_setup",
			"gcc_hr.gcc_hr_core.audit.log_doc_change",
		],
	},
	"HR Country Settings": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"HR Compliance Rule": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"HR Document Expiry Threshold": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"HR Compliance Score Band": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Employee Compliance Profile": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"GOSI Settings": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Saudization Requirement": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Government Submission Type": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Qatarization Requirement": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Emiratisation Requirement": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Omanisation Requirement": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Bahrainisation Requirement": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Kuwaitisation Requirement": {"on_update": "gcc_hr.gcc_hr_core.audit.log_doc_change"},
	"Salary Slip": {
		"on_submit": "gcc_hr.gcc_hr_core.payroll.sync_country_payroll",
	},
	"Payroll Entry": {
		"before_submit": "gcc_hr.gcc_hr_core.payroll.validate_payroll_compliance",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"gcc_hr.gcc_hr_core.compliance_engine.expiry_engine.run_daily_expiry_sweep",
		"gcc_hr.gcc_hr_core.compliance_engine.engine.run_daily_compliance_sweep",
		"gcc_hr.gcc_hr_core.workforce.run_daily_workforce_nationalization_recalculation",
	],
}

# Testing
# -------

# before_tests = "gcc_hr.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "gcc_hr.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "gcc_hr.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Employee": "gcc_hr.overrides.dashboard.get_dashboard_for_employee",
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["gcc_hr.utils.before_request"]
# after_request = ["gcc_hr.utils.after_request"]

# Job Events
# ----------
# before_job = ["gcc_hr.utils.before_job"]
# after_job = ["gcc_hr.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"gcc_hr.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

