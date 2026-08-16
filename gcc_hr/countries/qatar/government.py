# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Qatar's Government Submission Type generate/validate functions. Both
seeded submission types produce a document from data this app already has
(Qatarization Profile, Qatar Employee Profile) -- neither calls, nor
pretends to call, a real government API. Mirrors
countries/saudi_arabia/government.py's shape."""

import csv
import io

import frappe
from frappe.utils import get_datetime, now_datetime, today


def generate_qatarization_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> dict:
	profile_name = reference_name or company
	if not frappe.db.exists("Qatarization Profile", profile_name):
		frappe.throw(f"No Qatarization Profile found for {profile_name}. Run Recalculate on the Qatarization page first.")
	profile = frappe.get_doc("Qatarization Profile", profile_name)

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(
		[
			"Company",
			"Activity",
			"Business Size",
			"Total Employees",
			"Qatari Employees",
			"Non-Qatari Employees",
			"Qatari %",
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
			profile.qatari_employee_count,
			profile.non_qatari_employee_count,
			profile.qatari_percentage,
			profile.target_percentage,
			profile.gap,
			profile.compliance_status,
			today(),
		]
	)

	return {
		"filename": f"Qatarization-Report-{frappe.scrub(company)}-{today()}.csv",
		"content": buffer.getvalue(),
		"content_type": "text/csv",
	}


def validate_qatarization_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> list[str]:
	profile_name = reference_name or company
	if not frappe.db.exists("Qatarization Profile", profile_name):
		return [f"No Qatarization Profile found for {profile_name}."]

	last_calculation = frappe.db.get_value("Qatarization Profile", profile_name, "last_calculation")
	if not last_calculation:
		return ["Qatarization Profile has never been recalculated -- run Recalculate before submitting."]
	if (now_datetime() - get_datetime(last_calculation)).days > 30:
		return ["Qatarization Profile is more than 30 days stale -- run Recalculate before submitting."]
	return []


def generate_wps_report(company: str, reference_doctype: str | None = None, reference_name: str | None = None) -> dict:
	"""A worksheet of who is not yet WPS-registered -- meant to be actioned
	through the employer's bank/WPS portal by hand, not a claim that this
	app can register anyone with WPS itself."""
	employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, fields=["name", "employee_name"])
	employee_names = [e.name for e in employees]
	qatar_profiles = {
		p.employee: p
		for p in frappe.get_all(
			"Qatar Employee Profile",
			filters={"employee": ["in", employee_names or [""]]},
			fields=["employee", "wps_registered", "wps_bank_name"],
		)
	}

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow(["Employee", "Employee Name", "WPS Registered", "WPS Bank Name"])
	for emp in employees:
		profile = qatar_profiles.get(emp.name)
		writer.writerow(
			[
				emp.name,
				emp.employee_name,
				"Yes" if profile and profile.wps_registered else "No",
				profile.wps_bank_name if profile else "",
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
