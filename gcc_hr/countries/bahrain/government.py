# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Bahrain's Government Submission Type generate/validate functions. Both
seeded submission types produce a document from data this app already has
(Bahrainisation Profile, Bahrain Employee Profile) -- neither calls, nor
pretends to call, a real government API."""

import csv
import io

import frappe
from frappe.utils import get_datetime, now_datetime, today


def generate_bahrainisation_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> dict:
	profile_name = reference_name or company
	if not frappe.db.exists("Bahrainisation Profile", profile_name):
		frappe.throw(f"No Bahrainisation Profile found for {profile_name}. Run Recalculate on the Bahrainisation page first.")
	profile = frappe.get_doc("Bahrainisation Profile", profile_name)

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(
		[
			"Company",
			"Activity",
			"Business Size",
			"Total Employees",
			"Bahraini Employees",
			"Non-Bahraini Employees",
			"Bahraini %",
			"Target %",
			"Gap %",
			"Compliance Status",
			"As Of",
		]
	)
	writer.writerow(
		[
			profile.company,
			profile.activity or "",
			profile.business_size or "",
			profile.employee_count,
			profile.bahraini_employee_count,
			profile.non_bahraini_employee_count,
			profile.bahraini_percentage,
			profile.target_percentage,
			profile.gap,
			profile.compliance_status,
			today(),
		]
	)

	return {
		"filename": f"Bahrainisation-Report-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_bahrainisation_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> list[str]:
	profile_name = reference_name or company
	if not frappe.db.exists("Bahrainisation Profile", profile_name):
		return [f"No Bahrainisation Profile found for {profile_name}."]

	last_calculation = frappe.db.get_value("Bahrainisation Profile", profile_name, "last_calculation")
	if not last_calculation:
		return ["Bahrainisation Profile has never been recalculated -- run Recalculate before submitting."]
	if (now_datetime() - get_datetime(last_calculation)).days > 30:
		return ["Bahrainisation Profile is more than 30 days stale -- run Recalculate before submitting."]
	return []


def generate_sio_registration_summary(
	company: str, reference_doctype: str | None = None, reference_name: str | None = None
) -> dict:
	"""A worksheet of who still needs SIO registration -- meant to be taken
	to the Social Insurance Organisation and actioned by hand, not a claim
	that this app can register anyone with SIO itself."""
	employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, fields=["name", "employee_name"])
	employee_names = [e.name for e in employees]
	bahrain_profiles = {
		p.employee: p
		for p in frappe.get_all(
			"Bahrain Employee Profile",
			filters={"employee": ["in", employee_names or [""]]},
			fields=["employee", "sio_registered"],
		)
	}

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(["Employee", "Employee Name", "SIO Registered"])
	for emp in employees:
		profile = bahrain_profiles.get(emp.name)
		writer.writerow(
			[
				emp.name,
				emp.employee_name,
				"Yes" if profile and profile.sio_registered else "No",
			]
		)

	return {
		"filename": f"SIO-Registration-Worksheet-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_sio_registration_summary(
	company: str, reference_doctype: str | None = None, reference_name: str | None = None
) -> list[str]:
	if not frappe.db.exists("GCC HR Company Settings", company):
		return [f"{company} has no GCC HR Company Settings configured."]
	return []
