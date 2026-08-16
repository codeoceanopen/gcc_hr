# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Oman's HR Compliance Rule check_method implementations. Same fixed
signature as the other countries' rules.py: (employee, profile, rule) ->
(result, message, recommended_action).

check_passport_expiry/check_contract_active/check_contract_salary_match are
identical in shape to the other three countries' versions of the same
checks -- see ARCHITECTURE.md's note on this duplication (now a four-country
pattern)."""

import frappe
from frappe.utils import getdate, today


def _get_oman_profile(employee):
	if not frappe.db.exists("Oman Employee Profile", employee):
		return None
	return frappe.get_doc("Oman Employee Profile", employee)


def check_resident_card_expiry(employee, profile, rule):
	op = _get_oman_profile(employee)
	if not op:
		return ("Skipped", "No Oman Employee Profile found for this employee.", "")
	if op.nationality_status != "Non-Omani":
		return ("Passed", "Omani national -- resident card expiry not applicable.", "")
	if not op.resident_card_expiry:
		return (
			"Failed",
			"No resident card expiry date on file.",
			"Record the resident card expiry date on the Oman Employee Profile.",
		)

	days_remaining = (getdate(op.resident_card_expiry) - getdate(today())).days
	if days_remaining <= 0:
		return ("Failed", f"Resident card expired {abs(days_remaining)} day(s) ago.", "Renew the employee's resident card immediately.")
	if days_remaining <= 30:
		return ("Failed", f"Resident card expires in {days_remaining} day(s).", "Renew the employee's resident card before it expires.")
	return ("Passed", f"Resident card valid for {days_remaining} more day(s).", "")


def check_work_permit_expiry(employee, profile, rule):
	op = _get_oman_profile(employee)
	if not op:
		return ("Skipped", "No Oman Employee Profile found for this employee.", "")
	if op.nationality_status != "Non-Omani":
		return ("Passed", "Omani national -- work permit not applicable.", "")
	if not op.work_permit_expiry:
		return (
			"Failed",
			"No work permit expiry date on file.",
			"Record the work permit expiry date on the Oman Employee Profile.",
		)

	days_remaining = (getdate(op.work_permit_expiry) - getdate(today())).days
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


def check_non_omani_has_resident_card(employee, profile, rule):
	op = _get_oman_profile(employee)
	if not op:
		return ("Skipped", "No Oman Employee Profile found for this employee.", "")
	if op.nationality_status != "Non-Omani":
		return ("Passed", "Omani national.", "")
	if not op.resident_card_number:
		return (
			"Failed",
			"Non-Omani employee has no resident card number on file.",
			"Record the employee's resident card number on the Oman Employee Profile.",
		)
	return ("Passed", "Resident card number on file.", "")


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


def check_pasi_registered(employee, profile, rule):
	op = _get_oman_profile(employee)
	if not op:
		return ("Skipped", "No Oman Employee Profile found for this employee.", "")
	if not op.pasi_registered:
		return (
			"Failed",
			"Employee is not marked as registered with the Public Authority for Social Insurance (PASI).",
			"Register the employee with PASI / the Social Protection Fund.",
		)
	return ("Passed", "Employee is PASI-registered.", "")
