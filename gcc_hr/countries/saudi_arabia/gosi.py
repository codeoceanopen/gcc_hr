# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""GOSI (General Organization for Social Insurance) contribution
calculation. Dispatched from countries/saudi_arabia/payroll.py's
on_salary_slip_submit(), not wired to Salary Slip directly -- keeps all of
Saudi's payroll-submit side-effects in one place.

Rates/floor/ceiling are never hard-coded here -- see GOSI Settings,
effective-dated by gosi_settings.py:get_applicable_settings(). The pure
arithmetic (compute_contribution) is split out from the Salary-Slip-reading/
doctype-creating parts (calculate_for_salary_slip) so it can be unit tested
without needing a fully provisioned Salary Structure/Assignment/Slip --
that ERPNext payroll setup chain is exercised by the existing HRMS test
suite already; what's specific to this app is the contribution math.
"""

import frappe

from gcc_hr.saudi_arabia.doctype.gosi_settings.gosi_settings import get_applicable_settings


def compute_contribution(basic_salary: float, eligible_allowances: float, category: str, on_date) -> dict | None:
	"""Returns None if no GOSI Settings row applies on `on_date` for
	`category` (Saudi/Non-Saudi) -- otherwise a dict of settings_name/
	basic_salary/eligible_allowances/contribution_base/employee_contribution/
	employer_contribution/total_contribution."""
	settings = get_applicable_settings(category, on_date)
	if not settings:
		return None

	contribution_base = (basic_salary or 0) + (eligible_allowances or 0)
	if settings.contribution_floor:
		contribution_base = max(contribution_base, settings.contribution_floor)
	if settings.contribution_ceiling:
		contribution_base = min(contribution_base, settings.contribution_ceiling)

	employee_contribution = round(contribution_base * (settings.employee_contribution_rate or 0) / 100, 2)
	employer_contribution = round(contribution_base * (settings.employer_contribution_rate or 0) / 100, 2)

	return {
		"gosi_settings": settings.name,
		"basic_salary": basic_salary or 0,
		"eligible_allowances": eligible_allowances or 0,
		"contribution_base": contribution_base,
		"employee_contribution": employee_contribution,
		"employer_contribution": employer_contribution,
		"total_contribution": employee_contribution + employer_contribution,
	}


def calculate_for_salary_slip(salary_slip):
	employee = salary_slip.employee
	gosi_profile = frappe.db.get_value(
		"GOSI Employee Profile", employee, ["registration_status", "status"], as_dict=True
	)
	if not gosi_profile or gosi_profile.registration_status != "Registered" or gosi_profile.status != "Active":
		return None

	saudi_profile = frappe.db.get_value("Saudi Employee Profile", employee, "nationality_status")
	category = "Non-Saudi" if saudi_profile == "Non-Saudi" else "Saudi"

	basic_salary = _get_component_amount(salary_slip, "Basic")
	housing_allowance = _get_component_amount(
		salary_slip, "Housing Allowance"
	) or frappe.db.get_value("Employee Compliance Profile", employee, "housing_allowance") or 0

	result = compute_contribution(
		basic_salary, housing_allowance, category, salary_slip.posting_date or salary_slip.end_date
	)
	if not result:
		return None

	existing = frappe.db.exists("GOSI Payroll Calculation", {"salary_slip": salary_slip.name})
	if existing:
		return frappe.get_doc("GOSI Payroll Calculation", existing)

	calculation = frappe.get_doc({"doctype": "GOSI Payroll Calculation", "employee": employee, "salary_slip": salary_slip.name, **result})
	calculation.insert(ignore_permissions=True)
	return calculation


def _get_component_amount(salary_slip, component_name: str) -> float:
	for row in salary_slip.get("earnings") or []:
		if row.salary_component == component_name:
			return row.amount
	return 0


def get_gosi_status_summary(company: str) -> dict:
	"""Company-wide GOSI status for the Saudi dashboard's GOSI panel -- no
	such aggregate existed before (only per-employee GOSI Employee Profile
	fields, and government.py's generate_gosi_registration_summary which
	emits a CSV worksheet, not a summary dict). Counts active employees'
	registration_status, defaulting missing profiles to "Not Registered"
	the same way the CSV worksheet does."""
	employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, pluck="name")
	counts = dict.fromkeys(("Registered", "Pending", "Not Registered"), 0)
	if employees:
		registered = frappe.get_all(
			"GOSI Employee Profile",
			filters={"employee": ["in", employees]},
			group_by="registration_status",
			fields=["registration_status", {"COUNT": "*", "as": "count"}],
		)
		accounted_for = 0
		for row in registered:
			if row.registration_status in counts:
				counts[row.registration_status] = row.count
				accounted_for += row.count
		counts["Not Registered"] += len(employees) - accounted_for

	needs_review = counts["Pending"] + counts["Not Registered"]
	return {
		"total_employees": len(employees),
		"counts": counts,
		"needs_review": needs_review,
		"status": "Compliant" if needs_review == 0 else "Needs Review",
	}
