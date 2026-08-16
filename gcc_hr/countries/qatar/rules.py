# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Qatar's HR Compliance Rule check_method implementations. Same fixed
signature as countries/saudi_arabia/rules.py: (employee, profile, rule) ->
(result, message, recommended_action).

check_passport_expiry/check_contract_active/check_contract_salary_match are
identical in shape to Saudi's versions of the same checks -- genuinely
country-agnostic logic, duplicated here rather than shared, because sharing
would mean pointing this app's first two countries' seeded HR Compliance
Rule rows at each other's modules (confusing) or extracting them into a new
shared module and migrating Saudi's already-seeded rows to point at it
(a change to Saudi's shipped data, which this app avoids unless a third
country needs the exact same checks too -- see ARCHITECTURE.md's "Qatar
(Phase 6)" section)."""

import frappe
from frappe.utils import getdate, today


def _get_qatar_profile(employee):
	if not frappe.db.exists("Qatar Employee Profile", employee):
		return None
	return frappe.get_doc("Qatar Employee Profile", employee)


def check_qid_expiry(employee, profile, rule):
	qp = _get_qatar_profile(employee)
	if not qp:
		return ("Skipped", "No Qatar Employee Profile found for this employee.", "")
	if qp.nationality_status != "Non-Qatari":
		return ("Passed", "Qatari national -- QID not applicable.", "")
	if not qp.qid_expiry:
		return ("Failed", "No QID expiry date on file.", "Record the QID expiry date on the Qatar Employee Profile.")

	days_remaining = (getdate(qp.qid_expiry) - getdate(today())).days
	if days_remaining <= 0:
		return ("Failed", f"QID expired {abs(days_remaining)} day(s) ago.", "Renew the employee's QID immediately.")
	if days_remaining <= 30:
		return ("Failed", f"QID expires in {days_remaining} day(s).", "Renew the employee's QID before it expires.")
	return ("Passed", f"QID valid for {days_remaining} more day(s).", "")


def check_work_permit_expiry(employee, profile, rule):
	qp = _get_qatar_profile(employee)
	if not qp:
		return ("Skipped", "No Qatar Employee Profile found for this employee.", "")
	if qp.nationality_status != "Non-Qatari":
		return ("Passed", "Qatari national -- work permit not applicable.", "")
	if not qp.work_permit_expiry:
		return (
			"Failed",
			"No work permit expiry date on file.",
			"Record the work permit expiry date on the Qatar Employee Profile.",
		)

	days_remaining = (getdate(qp.work_permit_expiry) - getdate(today())).days
	if days_remaining <= 0:
		return (
			"Failed",
			f"Work permit expired {abs(days_remaining)} day(s) ago.",
			"Renew the employee's work permit immediately.",
		)
	if days_remaining <= 30:
		return (
			"Failed",
			f"Work permit expires in {days_remaining} day(s).",
			"Renew the employee's work permit before it expires.",
		)
	return ("Passed", f"Work permit valid for {days_remaining} more day(s).", "")


def check_passport_expiry(employee, profile, rule):
	if not profile.passport_expiry:
		return ("Skipped", "No passport expiry date on file.", "")

	days_remaining = (getdate(profile.passport_expiry) - getdate(today())).days
	if days_remaining <= 0:
		return ("Failed", f"Passport expired {abs(days_remaining)} day(s) ago.", "Renew the employee's passport immediately.")
	if days_remaining <= 90:
		return ("Failed", f"Passport expires in {days_remaining} day(s).", "Renew the employee's passport before it expires.")
	return ("Passed", f"Passport valid for {days_remaining} more day(s).", "")


def check_non_qatari_has_qid(employee, profile, rule):
	qp = _get_qatar_profile(employee)
	if not qp:
		return ("Skipped", "No Qatar Employee Profile found for this employee.", "")
	if qp.nationality_status != "Non-Qatari":
		return ("Passed", "Qatari national.", "")
	if not qp.qid_number:
		return (
			"Failed",
			"Non-Qatari employee has no QID number on file.",
			"Record the employee's QID number on the Qatar Employee Profile.",
		)
	return ("Passed", "QID number on file.", "")


def check_contract_active(employee, profile, rule):
	if not profile.contract:
		return ("Failed", "No employment contract linked on the Employee Compliance Profile.", "Link an active Contract.")

	contract = frappe.db.get_value("Contract", profile.contract, ["docstatus", "end_date"], as_dict=True)
	if not contract:
		return ("Failed", "Linked Contract no longer exists.", "Link a valid Contract.")
	if contract.docstatus != 1:
		return ("Failed", "Linked Contract is not signed/submitted.", "Submit the employment contract.")
	if contract.end_date and getdate(contract.end_date) < getdate(today()):
		return (
			"Failed",
			f"Contract expired on {contract.end_date}.",
			"Renew or replace the employee's contract before running payroll.",
		)
	return ("Passed", "Contract is active.", "")


def check_contract_salary_match(employee, profile, rule):
	if not profile.contract:
		return ("Skipped", "No employment contract linked -- salary match not checked.", "")

	contract_basic = frappe.db.get_value("Contract", profile.contract, "gcc_basic_salary")
	if not contract_basic:
		return ("Skipped", "Contract has no Basic Salary on file to compare against.", "")

	assignment_base = frappe.db.get_value(
		"Salary Structure Assignment",
		{"employee": employee, "docstatus": 1, "from_date": ["<=", today()]},
		"base",
		order_by="from_date desc",
	)
	if assignment_base is None:
		return ("Skipped", "No active Salary Structure Assignment found to compare against.", "")

	if abs(assignment_base - contract_basic) > 0.01:
		return (
			"Failed",
			f"Contract Basic Salary ({contract_basic}) does not match the active Salary Structure "
			f"Assignment's base salary ({assignment_base}).",
			"Review payroll before submission -- update the contract or the salary structure assignment.",
		)
	return ("Passed", "Contract Basic Salary matches the active Salary Structure Assignment.", "")


def check_wps_registered(employee, profile, rule):
	qp = _get_qatar_profile(employee)
	if not qp:
		return ("Skipped", "No Qatar Employee Profile found for this employee.", "")
	if not qp.wps_registered:
		return (
			"Failed",
			"Employee's salary is not marked as paid through a WPS-registered bank account.",
			"Register the employee's salary payment through the Wage Protection System (Law No. 17 of 2020).",
		)
	return ("Passed", "Employee is WPS-registered.", "")
