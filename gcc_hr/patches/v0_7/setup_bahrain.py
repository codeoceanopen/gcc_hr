# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Seeds Bahrain's HR Document Type/HR Compliance Rule/Gratuity Rule/
Bahrainisation Requirement/Government Submission Type rows and flips HR
Country Settings("Bahrain").compliance_engine_enabled on. Needed as an
explicit patch (not just the GCC HR Company Settings.on_update dispatch) so
that a company already pointed at Bahrain *before* this phase shipped
still gets Bahrain's rules. Same shape as v0_6/setup_oman.py."""

import frappe

from gcc_hr.countries.bahrain.employee import sync_employee
from gcc_hr.countries.bahrain.bahrainisation import recalculate
from gcc_hr.countries.bahrain.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Bahrain"):
		return
	setup()

	bahrain_companies = frappe.get_all("GCC HR Company Settings", filters={"country": "Bahrain"}, pluck="company")
	if not bahrain_companies:
		return

	for employee in frappe.get_all("Employee", filters={"company": ["in", bahrain_companies]}):
		sync_employee(employee)

	for company in bahrain_companies:
		recalculate(company)
