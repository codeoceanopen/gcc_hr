# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Seeds UAE's HR Document Type/HR Compliance Rule/Emiratisation
Requirement/Government Submission Type rows (and reuses hrms's own EOSB
Gratuity Rules -- see countries/united_arab_emirates/setup.py) and flips HR
Country Settings("United Arab Emirates").compliance_engine_enabled on.
Needed as an explicit patch (not just the GCC HR Company Settings.on_update
dispatch) so that a company already pointed at UAE *before* Phase 7 shipped
still gets UAE's rules. Mirrors v0_4/setup_qatar.py's shape."""

import frappe

from gcc_hr.countries.united_arab_emirates.emiratisation import recalculate
from gcc_hr.countries.united_arab_emirates.employee import sync_employee
from gcc_hr.countries.united_arab_emirates.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "United Arab Emirates"):
		return
	setup()

	uae_companies = frappe.get_all("GCC HR Company Settings", filters={"country": "United Arab Emirates"}, pluck="company")
	if not uae_companies:
		return

	for employee in frappe.get_all("Employee", filters={"company": ["in", uae_companies]}):
		sync_employee(employee)

	for company in uae_companies:
		recalculate(company)
