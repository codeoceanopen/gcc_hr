# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Saudi Arabia's HR Compliance Rule check_method implementations. Each rule
row (seeded by setup.py) points at one of these by dotted path. Signature is
fixed by gcc_hr_core/compliance_engine/engine.py: (employee, profile, rule)
-> (result, message, recommended_action), result in Passed/Failed/Skipped.
`profile` is the Employee Compliance Profile document (already loaded by
the engine, so its fetched fields like passport_expiry are free to read)."""

import frappe
from frappe.utils import getdate, today


def _get_saudi_profile(employee):
	if not frappe.db.exists("Saudi Employee Profile", employee):
		return None
	return frappe.get_doc("Saudi Employee Profile", employee)


def check_iqama_expiry(employee, profile, rule):
	sp = _get_saudi_profile(employee)
	if not sp:
		return ("Skipped", "No Saudi Employee Profile found for this employee.", "")
	if sp.nationality_status != "Non-Saudi":
		return ("Passed", "Saudi national -- Iqama not applicable.", "")
	if not sp.iqama_expiry:
		return ("Failed", "No Iqama expiry date on file.", "Record the Iqama expiry date on the Saudi Employee Profile.")

	days_remaining = (getdate(sp.iqama_expiry) - getdate(today())).days
	if days_remaining <= 0:
		return ("Failed", f"Iqama expired {abs(days_remaining)} day(s) ago.", "Renew the employee's Iqama immediately.")
	if days_remaining <= 30:
		return ("Failed", f"Iqama expires in {days_remaining} day(s).", "Renew the employee's Iqama before it expires.")
	return ("Passed", f"Iqama valid for {days_remaining} more day(s).", "")


def check_work_permit_expiry(employee, profile, rule):
	sp = _get_saudi_profile(employee)
	if not sp:
		return ("Skipped", "No Saudi Employee Profile found for this employee.", "")
	if sp.nationality_status != "Non-Saudi":
		return ("Passed", "Saudi national -- work permit not applicable.", "")
	if not sp.work_permit_expiry:
		return (
			"Failed",
			"No work permit expiry date on file.",
			"Record the work permit expiry date on the Saudi Employee Profile.",
		)

	days_remaining = (getdate(sp.work_permit_expiry) - getdate(today())).days
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


def check_non_saudi_has_iqama(employee, profile, rule):
	sp = _get_saudi_profile(employee)
	if not sp:
		return ("Skipped", "No Saudi Employee Profile found for this employee.", "")
	if sp.nationality_status != "Non-Saudi":
		return ("Passed", "Saudi national.", "")
	if not sp.iqama_number:
		return (
			"Failed",
			"Non-Saudi employee has no Iqama number on file.",
			"Record the employee's Iqama number on the Saudi Employee Profile.",
		)
	return ("Passed", "Iqama number on file.", "")


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


def check_gosi_registered(employee, profile, rule):
	registration_status = frappe.db.get_value("GOSI Employee Profile", employee, "registration_status")
	if registration_status is None:
		return ("Failed", "No GOSI Employee Profile found for this employee.", "Create a GOSI Employee Profile and register the employee.")
	if registration_status != "Registered":
		return (
			"Failed",
			f"GOSI registration status is '{registration_status}', not Registered.",
			"Complete GOSI registration for this employee before running payroll.",
		)
	return ("Passed", "Employee is registered with GOSI.", "")


def check_annual_leave_entitlement(employee, profile, rule):
	from gcc_hr.countries.saudi_arabia.leave import (
		ANNUAL_LEAVE_TYPE,
		get_annual_leave_entitlement,
		get_latest_annual_leave_allocation,
	)

	date_of_joining = frappe.db.get_value("Employee", employee, "date_of_joining")
	entitlement = get_annual_leave_entitlement(date_of_joining)

	allocation = get_latest_annual_leave_allocation(employee)
	if not allocation:
		return (
			"Skipped",
			f"No submitted '{ANNUAL_LEAVE_TYPE}' Leave Allocation found for this employee.",
			"",
		)

	allocated = allocation["new_leaves_allocated"] or 0
	if allocated < entitlement:
		return (
			"Failed",
			f"Latest annual leave allocation is {allocated} day(s), below the {entitlement}-day entitlement "
			"for this employee's tenure (KSA Labour Law Art. 109).",
			f"Allocate at least {entitlement} days of {ANNUAL_LEAVE_TYPE} for this employee.",
		)
	return ("Passed", f"Annual leave allocation ({allocated} days) meets the {entitlement}-day entitlement.", "")
