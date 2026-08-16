# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Seeds Oman's HR Document Type/HR Compliance Rule/Gratuity Rule/
Omanisation Requirement/Government Submission Type rows and flips HR
Country Settings("Oman").compliance_engine_enabled on. Needed as an explicit
patch (not just the GCC HR Company Settings.on_update dispatch) so that a
company already pointed at Oman *before* Phase 8 shipped still gets Oman's
rules. Same shape as v0_4/setup_qatar.py."""

import frappe

from gcc_hr.countries.oman.employee import sync_employee
from gcc_hr.countries.oman.omanisation import recalculate
from gcc_hr.countries.oman.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Oman"):
		return
	setup()

	oman_companies = frappe.get_all("GCC HR Company Settings", filters={"country": "Oman"}, pluck="company")
	if not oman_companies:
		return

	for employee in frappe.get_all("Employee", filters={"company": ["in", oman_companies]}):
		sync_employee(employee)

	for company in oman_companies:
		recalculate(company)
