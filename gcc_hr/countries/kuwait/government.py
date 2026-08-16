# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Kuwait's Government Submission Type generate/validate functions. Both
seeded submission types produce a document from data this app already has
(Kuwaitisation Profile, Kuwait Employee Profile) -- neither calls, nor
pretends to call, a real government API. Mirrors
countries/oman/government.py's shape; the WPS worksheet functions mirror
countries/qatar/government.py's generate_wps_report shape."""

import csv
import io

import frappe
from frappe.utils import get_datetime, now_datetime, today


def generate_kuwaitisation_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> dict:
	profile_name = reference_name or company
	if not frappe.db.exists("Kuwaitisation Profile", profile_name):
		frappe.throw(f"No Kuwaitisation Profile found for {profile_name}. Run Recalculate on the Kuwaitisation page first.")
	profile = frappe.get_doc("Kuwaitisation Profile", profile_name)

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(
		[
			"Company",
			"Activity",
			"Business Size",
			"Total Employees",
			"Kuwaiti Employees",
			"Non-Kuwaiti Employees",
			"Kuwaiti %",
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
			profile.kuwaiti_employee_count,
			profile.non_kuwaiti_employee_count,
			profile.kuwaiti_percentage,
			profile.target_percentage,
			profile.gap,
			profile.compliance_status,
			today(),
		]
	)

	return {
		"filename": f"Kuwaitisation-Report-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_kuwaitisation_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> list[str]:
	profile_name = reference_name or company
	if not frappe.db.exists("Kuwaitisation Profile", profile_name):
		return [f"No Kuwaitisation Profile found for {profile_name}."]

	last_calculation = frappe.db.get_value("Kuwaitisation Profile", profile_name, "last_calculation")
	if not last_calculation:
		return ["Kuwaitisation Profile has never been recalculated -- run Recalculate before submitting."]
	if (now_datetime() - get_datetime(last_calculation)).days > 30:
		return ["Kuwaitisation Profile is more than 30 days stale -- run Recalculate before submitting."]
	return []


def generate_wps_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> dict:
	"""A worksheet of who is not yet WPS-registered -- meant to be actioned
	through the employer's bank/WPS portal by hand, not a claim that this
	app can register anyone with WPS itself."""
	employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, fields=["name", "employee_name"])
	employee_names = [e.name for e in employees]
	kuwait_profiles = {
		p.employee: p
		for p in frappe.get_all(
			"Kuwait Employee Profile",
			filters={"employee": ["in", employee_names or [""]]},
			fields=["employee", "wps_registered"],
		)
	}

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(["Employee", "Employee Name", "WPS Registered"])
	for emp in employees:
		profile = kuwait_profiles.get(emp.name)
		writer.writerow(
			[
				emp.name,
				emp.employee_name,
				"Yes" if profile and profile.wps_registered else "No",
			]
		)

	return {
		"filename": f"WPS-Registration-Worksheet-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_wps_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> list[str]:
	if not frappe.db.exists("GCC HR Company Settings", company):
		return [f"{company} has no GCC HR Company Settings configured."]
	return []
