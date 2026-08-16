# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


@frappe.whitelist()
def recalculate_now(company: str):
	"""Backs the Kuwaitisation page's [Recalculate] action."""
	if not frappe.has_permission("Kuwaitisation Profile", "write", doc=company if frappe.db.exists("Kuwaitisation Profile", company) else None):
		frappe.throw(frappe._("Not permitted to recalculate Kuwaitisation for this company."), frappe.PermissionError)
	enforce_company_country(company, "Kuwait")

	from gcc_hr.countries.kuwait.kuwaitisation import recalculate

	profile = recalculate(company)
	return profile.name


@frappe.whitelist()
def simulate(company: str, hire_kuwaiti=0, hire_non_kuwaiti=0, terminate_kuwaiti=0, terminate_non_kuwaiti=0):
	"""Backs the What-If Simulator -- pure projection, never touches real
	Employee/Kuwait Employee Profile data."""
	if not frappe.has_permission("Kuwaitisation Profile", "read"):
		frappe.throw(frappe._("Not permitted to view Kuwaitisation data."), frappe.PermissionError)
	enforce_company_country(company, "Kuwait")

	from gcc_hr.countries.kuwait.kuwaitisation import simulate as simulate_kuwaitisation

	return simulate_kuwaitisation(
		company,
		hire_kuwaiti=int(hire_kuwaiti or 0),
		hire_non_kuwaiti=int(hire_non_kuwaiti or 0),
		terminate_kuwaiti=int(terminate_kuwaiti or 0),
		terminate_non_kuwaiti=int(terminate_non_kuwaiti or 0),
	)
