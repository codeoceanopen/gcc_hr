# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


@frappe.whitelist()
def recalculate_now(company: str):
	"""Backs the Qatarization page's [Recalculate] action."""
	if not frappe.has_permission("Qatarization Profile", "write", doc=company if frappe.db.exists("Qatarization Profile", company) else None):
		frappe.throw(frappe._("Not permitted to recalculate Qatarization for this company."), frappe.PermissionError)
	enforce_company_country(company, "Qatar")

	from gcc_hr.countries.qatar.qatarization import recalculate

	profile = recalculate(company)
	return profile.name


@frappe.whitelist()
def simulate(company: str, hire_qatari=0, hire_non_qatari=0, terminate_qatari=0, terminate_non_qatari=0):
	"""Backs the What-If Simulator -- pure projection, never touches real
	Employee/Qatar Employee Profile data."""
	if not frappe.has_permission("Qatarization Profile", "read"):
		frappe.throw(frappe._("Not permitted to view Qatarization data."), frappe.PermissionError)
	enforce_company_country(company, "Qatar")

	from gcc_hr.countries.qatar.qatarization import simulate as simulate_qatarization

	return simulate_qatarization(
		company,
		hire_qatari=int(hire_qatari or 0),
		hire_non_qatari=int(hire_non_qatari or 0),
		terminate_qatari=int(terminate_qatari or 0),
		terminate_non_qatari=int(terminate_non_qatari or 0),
	)
