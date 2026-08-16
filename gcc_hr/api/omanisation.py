# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


@frappe.whitelist()
def recalculate_now(company: str):
	"""Backs the Omanisation page's [Recalculate] action."""
	if not frappe.has_permission("Omanisation Profile", "write", doc=company if frappe.db.exists("Omanisation Profile", company) else None):
		frappe.throw(frappe._("Not permitted to recalculate Omanisation for this company."), frappe.PermissionError)
	enforce_company_country(company, "Oman")

	from gcc_hr.countries.oman.omanisation import recalculate

	profile = recalculate(company)
	return profile.name


@frappe.whitelist()
def simulate(company: str, hire_omani=0, hire_non_omani=0, terminate_omani=0, terminate_non_omani=0):
	"""Backs the What-If Simulator -- pure projection, never touches real
	Employee/Oman Employee Profile data."""
	if not frappe.has_permission("Omanisation Profile", "read"):
		frappe.throw(frappe._("Not permitted to view Omanisation data."), frappe.PermissionError)
	enforce_company_country(company, "Oman")

	from gcc_hr.countries.oman.omanisation import simulate as simulate_omanisation

	return simulate_omanisation(
		company,
		hire_omani=int(hire_omani or 0),
		hire_non_omani=int(hire_non_omani or 0),
		terminate_omani=int(terminate_omani or 0),
		terminate_non_omani=int(terminate_non_omani or 0),
	)
