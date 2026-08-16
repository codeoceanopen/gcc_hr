# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


@frappe.whitelist()
def recalculate_now(company: str):
	"""Backs the Emiratisation page's [Recalculate] action."""
	if not frappe.has_permission("Emiratisation Profile", "write", doc=company if frappe.db.exists("Emiratisation Profile", company) else None):
		frappe.throw(frappe._("Not permitted to recalculate Emiratisation for this company."), frappe.PermissionError)
	enforce_company_country(company, "United Arab Emirates")

	from gcc_hr.countries.united_arab_emirates.emiratisation import recalculate

	profile = recalculate(company)
	return profile.name


@frappe.whitelist()
def simulate(company: str, hire_emirati=0, hire_non_emirati=0, terminate_emirati=0, terminate_non_emirati=0):
	"""Backs the What-If Simulator -- pure projection, never touches real
	Employee/UAE Employee Profile data."""
	if not frappe.has_permission("Emiratisation Profile", "read"):
		frappe.throw(frappe._("Not permitted to view Emiratisation data."), frappe.PermissionError)
	enforce_company_country(company, "United Arab Emirates")

	from gcc_hr.countries.united_arab_emirates.emiratisation import simulate as simulate_emiratisation

	return simulate_emiratisation(
		company,
		hire_emirati=int(hire_emirati or 0),
		hire_non_emirati=int(hire_non_emirati or 0),
		terminate_emirati=int(terminate_emirati or 0),
		terminate_non_emirati=int(terminate_non_emirati or 0),
	)
