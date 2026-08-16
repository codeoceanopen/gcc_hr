# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Seeds Qatar's HR Document Type/HR Compliance Rule/Gratuity Rule/
Qatarization Requirement/Government Submission Type rows and flips HR
Country Settings("Qatar").compliance_engine_enabled on. Needed as an
explicit patch (not just the GCC HR Company Settings.on_update dispatch) so
that a company already pointed at Qatar *before* Phase 6 shipped still gets
Qatar's rules -- the on_update dispatch only fires when the country field
actually changes. Combines what were three separate Saudi patches (v0_0/
v0_1/v0_2 equivalents) into one, since Qatar's whole localization/payroll/
workforce package ships in a single phase."""

import frappe

from gcc_hr.countries.qatar.employee import sync_employee
from gcc_hr.countries.qatar.qatarization import recalculate
from gcc_hr.countries.qatar.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Qatar"):
		return
	setup()

	qatar_companies = frappe.get_all("GCC HR Company Settings", filters={"country": "Qatar"}, pluck="company")
	if not qatar_companies:
		return

	for employee in frappe.get_all("Employee", filters={"company": ["in", qatar_companies]}):
		sync_employee(employee)

	for company in qatar_companies:
		recalculate(company)
