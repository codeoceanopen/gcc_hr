# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Seeds Saudi Arabia's HR Document Type/HR Compliance Rule rows and flips
HR Country Settings("Saudi Arabia").compliance_engine_enabled on. Needed as
an explicit patch (not just the GCC HR Company Settings.on_update dispatch)
so that a company already pointed at Saudi Arabia *before* this app's
Phase 2 shipped still gets Saudi's rules -- the on_update dispatch only
fires when the country field actually changes."""

import frappe

from gcc_hr.countries.saudi_arabia.employee import sync_employee
from gcc_hr.countries.saudi_arabia.setup import setup


def execute():
	if not frappe.db.exists("HR Country Settings", "Saudi Arabia"):
		return
	setup()
	backfill_saudi_employee_profiles()


def backfill_saudi_employee_profiles():
	saudi_companies = frappe.get_all(
		"GCC HR Company Settings", filters={"country": "Saudi Arabia"}, pluck="company"
	)
	if not saudi_companies:
		return
	for employee in frappe.get_all("Employee", filters={"company": ["in", saudi_companies]}):
		sync_employee(employee)
