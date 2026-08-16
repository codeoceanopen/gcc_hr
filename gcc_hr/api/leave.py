# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


@frappe.whitelist()
def get_leave_summary(company: str):
	"""Backs the Saudi Leave page's entitlement/carry-forward table."""
	if not frappe.has_permission("Leave Allocation", "read"):
		frappe.throw(frappe._("Not permitted to view leave data."), frappe.PermissionError)
	enforce_company_country(company, "Saudi Arabia")

	from gcc_hr.countries.saudi_arabia.leave import get_leave_summary as get_summary

	return get_summary(company)
