# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe

from gcc_hr.gcc_hr_core.compliance_engine.engine import run_compliance_check


@frappe.whitelist()
def run_compliance_check_for_employee(employee: str):
	"""Backs the Employee Compliance Profile detail page's [Run Compliance
	Check] action (see product brief section 25). A thin wrapper is needed
	here only because the engine itself isn't whitelisted -- everything else
	on that page is plain frappe.client.* CRUD via frappe-ui."""
	if not frappe.has_permission("Employee Compliance Profile", "write", doc=employee):
		frappe.throw(frappe._("Not permitted to run a compliance check for this employee."), frappe.PermissionError)
	check = run_compliance_check(employee, reason="Manual")
	if not check:
		frappe.throw(frappe._("No country configured for this employee's company."))
	return check.name
