# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Payroll-adjacent hooks. Extends standard Frappe HR payroll (Salary Slip,
Payroll Entry) rather than building a parallel payroll engine -- see
ARCHITECTURE.md's "why reuse instead of duplicate"."""

import frappe
from frappe import _

from gcc_hr.countries import get_country_attr
from gcc_hr.gcc_hr_core.compliance_engine.engine import run_compliance_check
from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import get_company_settings


def sync_country_payroll(doc, method=None):
	"""Salary Slip.on_submit hook -- give the employee's country package a
	chance to run its own payroll side-effects (e.g. Saudi's GOSI
	calculation). No-op for countries that don't implement payroll.py yet."""
	country = frappe.db.get_value("Employee Compliance Profile", doc.employee, "country")
	if not country:
		return
	on_submit_fn = get_country_attr(country, "payroll", "on_salary_slip_submit")
	if on_submit_fn:
		on_submit_fn(doc)


def validate_payroll_compliance(doc, method=None):
	"""Payroll Entry.before_submit hook -- runs the compliance engine for
	every employee in the run, records a Payroll Compliance Check, and
	blocks submission if GCC HR Company Settings.payroll_compliance_required
	is set and any employee has a Critical/Blocking issue."""
	company_settings = get_company_settings(doc.company)
	if not company_settings or not company_settings.get("country"):
		return  # company not configured for GCC HR at all -- nothing to check

	employees = [row.employee for row in doc.employees]
	if not employees:
		return

	rows = []
	passed = warnings = critical = 0
	for employee in employees:
		check = run_compliance_check(employee, reason="Payroll")
		if not check:
			continue
		rows.append({"employee": employee, "compliance_check": check.name})
		if check.critical_issues:
			critical += 1
		elif check.warnings:
			warnings += 1
		else:
			passed += 1

	status = "Blocked" if critical else ("Warnings" if warnings else "Passed")

	pcc = frappe.get_doc(
		{
			"doctype": "Payroll Compliance Check",
			"payroll_entry": doc.name,
			"total_employees": len(rows),
			"passed": passed,
			"warnings": warnings,
			"critical": critical,
			"status": status,
			"employees": rows,
		}
	)
	pcc.insert(ignore_permissions=True)

	if critical and company_settings.payroll_compliance_required:
		frappe.throw(
			_(
				"Payroll Compliance Check {0} found critical issues for {1} employee(s). "
				"Resolve them, or disable Payroll Compliance Required on GCC HR Company "
				"Settings to submit anyway."
			).format(frappe.bold(pcc.name), critical),
			title=_("Payroll Blocked by Compliance"),
		)
