# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


@frappe.whitelist()
def recalculate_now(company: str):
	"""Backs the Saudization page's [Recalculate] action."""
	if not frappe.has_permission("Saudization Profile", "write", doc=company if frappe.db.exists("Saudization Profile", company) else None):
		frappe.throw(frappe._("Not permitted to recalculate Saudization for this company."), frappe.PermissionError)
	enforce_company_country(company, "Saudi Arabia")

	from gcc_hr.countries.saudi_arabia.saudization import recalculate

	profile = recalculate(company)
	return profile.name


@frappe.whitelist()
def simulate(company: str, hire_saudi=0, hire_non_saudi=0, terminate_saudi=0, terminate_non_saudi=0):
	"""Backs the What-If Simulator -- pure projection, never touches real
	Employee/Saudi Employee Profile data."""
	if not frappe.has_permission("Saudization Profile", "read"):
		frappe.throw(frappe._("Not permitted to view Saudization data."), frappe.PermissionError)
	enforce_company_country(company, "Saudi Arabia")

	from gcc_hr.countries.saudi_arabia.saudization import simulate as simulate_saudization

	return simulate_saudization(
		company,
		hire_saudi=int(hire_saudi or 0),
		hire_non_saudi=int(hire_non_saudi or 0),
		terminate_saudi=int(terminate_saudi or 0),
		terminate_non_saudi=int(terminate_non_saudi or 0),
	)


@frappe.whitelist()
def get_gosi_summary(company: str):
	"""Backs the Saudi dashboard's GOSI panel."""
	if not frappe.has_permission("GOSI Employee Profile", "read"):
		frappe.throw(frappe._("Not permitted to view GOSI data."), frappe.PermissionError)
	enforce_company_country(company, "Saudi Arabia")

	from gcc_hr.countries.saudi_arabia.gosi import get_gosi_status_summary

	return get_gosi_status_summary(company)
