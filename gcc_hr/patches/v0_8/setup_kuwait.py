# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Seeds Kuwait's HR Document Type/HR Compliance Rule/Gratuity Rule/
Kuwaitisation Requirement/Government Submission Type rows and flips HR
Country Settings("Kuwait").compliance_engine_enabled on. Needed as an
explicit patch (not just the GCC HR Company Settings.on_update dispatch) so
that a company already pointed at Kuwait *before* this phase shipped still
gets Kuwait's rules. Same shape as v0_6/setup_oman.py."""

import frappe

from gcc_hr.countries.kuwait.employee import sync_employee
from gcc_hr.countries.kuwait.kuwaitisation import recalculate
from gcc_hr.countries.kuwait.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Kuwait"):
		return
	setup()

	kuwait_companies = frappe.get_all("GCC HR Company Settings", filters={"country": "Kuwait"}, pluck="company")
	if not kuwait_companies:
		return

	for employee in frappe.get_all("Employee", filters={"company": ["in", kuwait_companies]}):
		sync_employee(employee)

	for company in kuwait_companies:
		recalculate(company)
