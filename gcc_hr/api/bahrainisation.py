# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


@frappe.whitelist()
def recalculate_now(company: str):
	"""Backs the Bahrainisation page's [Recalculate] action."""
	if not frappe.has_permission("Bahrainisation Profile", "write", doc=company if frappe.db.exists("Bahrainisation Profile", company) else None):
		frappe.throw(frappe._("Not permitted to recalculate Bahrainisation for this company."), frappe.PermissionError)
	enforce_company_country(company, "Bahrain")

	from gcc_hr.countries.bahrain.bahrainisation import recalculate

	profile = recalculate(company)
	return profile.name


@frappe.whitelist()
def simulate(company: str, hire_bahraini=0, hire_non_bahraini=0, terminate_bahraini=0, terminate_non_bahraini=0):
	"""Backs the What-If Simulator -- pure projection, never touches real
	Employee/Bahrain Employee Profile data."""
	if not frappe.has_permission("Bahrainisation Profile", "read"):
		frappe.throw(frappe._("Not permitted to view Bahrainisation data."), frappe.PermissionError)
	enforce_company_country(company, "Bahrain")

	from gcc_hr.countries.bahrain.bahrainisation import simulate as simulate_bahrainisation

	return simulate_bahrainisation(
		company,
		hire_bahraini=int(hire_bahraini or 0),
		hire_non_bahraini=int(hire_non_bahraini or 0),
		terminate_bahraini=int(terminate_bahraini or 0),
		terminate_non_bahraini=int(terminate_non_bahraini or 0),
	)
