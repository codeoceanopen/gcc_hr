# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Oman's Government Submission Type generate/validate functions. Both
seeded submission types produce a document from data this app already has
(Omanisation Profile, Oman Employee Profile) -- neither calls, nor pretends
to call, a real government API."""

import csv
import io

import frappe
from frappe.utils import get_datetime, now_datetime, today


def generate_omanisation_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> dict:
	profile_name = reference_name or company
	if not frappe.db.exists("Omanisation Profile", profile_name):
		frappe.throw(f"No Omanisation Profile found for {profile_name}. Run Recalculate on the Omanisation page first.")
	profile = frappe.get_doc("Omanisation Profile", profile_name)

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(
		[
			"Company",
			"Activity",
			"Business Size",
			"Total Employees",
			"Omani Employees",
			"Non-Omani Employees",
			"Omani %",
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
			profile.omani_employee_count,
			profile.non_omani_employee_count,
			profile.omani_percentage,
			profile.target_percentage,
			profile.gap,
			profile.compliance_status,
			today(),
		]
	)

	return {
		"filename": f"Omanisation-Report-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_omanisation_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> list[str]:
	profile_name = reference_name or company
	if not frappe.db.exists("Omanisation Profile", profile_name):
		return [f"No Omanisation Profile found for {profile_name}."]

	last_calculation = frappe.db.get_value("Omanisation Profile", profile_name, "last_calculation")
	if not last_calculation:
		return ["Omanisation Profile has never been recalculated -- run Recalculate before submitting."]
	if (now_datetime() - get_datetime(last_calculation)).days > 30:
		return ["Omanisation Profile is more than 30 days stale -- run Recalculate before submitting."]
	return []


def generate_pasi_registration_summary(
	company: str, reference_doctype: str | None = None, reference_name: str | None = None
) -> dict:
	"""A worksheet of who still needs PASI registration -- meant to be taken
	to the Public Authority for Social Insurance and actioned by hand, not a
	claim that this app can register anyone with PASI itself."""
	employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, fields=["name", "employee_name"])
	employee_names = [e.name for e in employees]
	oman_profiles = {
		p.employee: p
		for p in frappe.get_all(
			"Oman Employee Profile",
			filters={"employee": ["in", employee_names or [""]]},
			fields=["employee", "pasi_registered"],
		)
	}

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(["Employee", "Employee Name", "PASI Registered"])
	for emp in employees:
		profile = oman_profiles.get(emp.name)
		writer.writerow(
			[
				emp.name,
				emp.employee_name,
				"Yes" if profile and profile.pasi_registered else "No",
			]
		)

	return {
		"filename": f"PASI-Registration-Worksheet-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_pasi_registration_summary(
	company: str, reference_doctype: str | None = None, reference_name: str | None = None
) -> list[str]:
	if not frappe.db.exists("GCC HR Company Settings", company):
		return [f"{company} has no GCC HR Company Settings configured."]
	return []
