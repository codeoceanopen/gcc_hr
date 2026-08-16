# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Saudi Arabia's Government Submission Type generate/validate functions.
Both seeded submission types produce a document from data this app already
has (Saudization Profile from Phase 4, GOSI Employee Profile from Phase 3) --
neither calls, nor pretends to call, a real government API. See
gcc_hr_core/government.py's module docstring and SECURITY.md."""

import csv
import io

import frappe
from frappe.utils import get_datetime, now_datetime, today


def generate_nitaqat_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> dict:
	profile_name = reference_name or company
	if not frappe.db.exists("Saudization Profile", profile_name):
		frappe.throw(f"No Saudization Profile found for {profile_name}. Run Recalculate on the Saudization page first.")
	profile = frappe.get_doc("Saudization Profile", profile_name)

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(
		[
			"Company",
			"Activity",
			"Business Size",
			"Total Employees",
			"Saudi Employees",
			"Non-Saudi Employees",
			"Saudi %",
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
			profile.saudi_employee_count,
			profile.non_saudi_employee_count,
			profile.saudi_percentage,
			profile.target_percentage,
			profile.gap,
			profile.compliance_status,
			today(),
		]
	)

	return {
		"filename": f"Nitaqat-Report-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_nitaqat_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> list[str]:
	profile_name = reference_name or company
	if not frappe.db.exists("Saudization Profile", profile_name):
		return [f"No Saudization Profile found for {profile_name}."]

	last_calculation = frappe.db.get_value("Saudization Profile", profile_name, "last_calculation")
	if not last_calculation:
		return ["Saudization Profile has never been recalculated -- run Recalculate before submitting."]
	if (now_datetime() - get_datetime(last_calculation)).days > 30:
		return ["Saudization Profile is more than 30 days stale -- run Recalculate before submitting."]
	return []


def generate_gosi_registration_summary(
	company: str, reference_doctype: str | None = None, reference_name: str | None = None
) -> dict:
	"""A worksheet of who still needs GOSI registration -- meant to be taken
	to gosi.gov.sa and actioned by hand, not a claim that this app can
	register anyone with GOSI itself."""
	employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, fields=["name", "employee_name"])
	employee_names = [e.name for e in employees]
	gosi_profiles = {
		p.employee: p
		for p in frappe.get_all(
			"GOSI Employee Profile",
			filters={"employee": ["in", employee_names or [""]]},
			fields=["employee", "registration_status", "gosi_number"],
		)
	}

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(["Employee", "Employee Name", "GOSI Registration Status", "GOSI Number"])
	for emp in employees:
		profile = gosi_profiles.get(emp.name)
		writer.writerow(
			[
				emp.name,
				emp.employee_name,
				profile.registration_status if profile else "Not Registered",
				profile.gosi_number if profile else "",
			]
		)

	return {
		"filename": f"GOSI-Registration-Worksheet-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_gosi_registration_summary(
	company: str, reference_doctype: str | None = None, reference_name: str | None = None
) -> list[str]:
	if not frappe.db.exists("GCC HR Company Settings", company):
		return [f"{company} has no GCC HR Company Settings configured."]
	return []
