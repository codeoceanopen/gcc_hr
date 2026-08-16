# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Kuwaitisation workforce-nationalization tracking. Mirrors
countries/saudi_arabia/saudization.py's shape exactly (target lookup by
specificity, active-employee counts, risk band, pure what-if simulator).
Kuwaitisation is Kuwait's sector-specific quota program administered by the
Public Authority for Manpower, the same general shape as Omanisation/
Bahrainisation/Emiratisation/Qatarization, but Kuwaitisation Requirement's
seeded row is still an illustrative placeholder -- see that doctype's own
description field."""

import frappe
from frappe.utils import flt, getdate, now_datetime, today

AT_RISK_TOLERANCE = 2.0


def get_applicable_target(company: str, activity: str | None, business_size: str | None, on_date=None) -> float | None:
	on_date = getdate(on_date or today())
	rows = frappe.get_all(
		"Kuwaitisation Requirement",
		filters={"effective_from": ["<=", on_date]},
		fields=["name", "company", "activity", "business_size", "target_percentage", "effective_from", "effective_to"],
		order_by="effective_from desc",
	)
	rows = [r for r in rows if not r.effective_to or getdate(r.effective_to) >= on_date]

	for row in rows:  # 1. exact company match
		if row.company == company:
			return row.target_percentage
	for row in rows:  # 2. activity + business_size match
		if row.company:
			continue
		if activity and row.activity == activity and business_size and row.business_size == business_size:
			return row.target_percentage
	for row in rows:  # 3. global fallback (blank company/activity/business_size)
		if not row.company and not row.activity and not row.business_size:
			return row.target_percentage
	return None


def get_workforce_counts(company: str) -> dict:
	employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, pluck="name")
	if not employees:
		return {"employee_count": 0, "kuwaiti_employee_count": 0, "non_kuwaiti_employee_count": 0}

	kuwaiti_count = frappe.db.count(
		"Kuwait Employee Profile", {"employee": ["in", employees], "nationality_status": "Kuwaiti"}
	)
	non_kuwaiti_count = frappe.db.count(
		"Kuwait Employee Profile", {"employee": ["in", employees], "nationality_status": "Non-Kuwaiti"}
	)
	return {
		"employee_count": len(employees),
		"kuwaiti_employee_count": kuwaiti_count,
		"non_kuwaiti_employee_count": non_kuwaiti_count,
	}


def compute_status(kuwaiti_percentage: float, target_percentage: float | None) -> str:
	if target_percentage is None:
		return "Compliant"  # nothing configured to fall short of
	if kuwaiti_percentage >= target_percentage:
		return "Compliant"
	if kuwaiti_percentage >= target_percentage - AT_RISK_TOLERANCE:
		return "At Risk"
	return "Non-Compliant"


def recalculate(company: str):
	counts = get_workforce_counts(company)
	kuwaiti_percentage = (
		round(counts["kuwaiti_employee_count"] / counts["employee_count"] * 100, 2) if counts["employee_count"] else 0.0
	)

	if not frappe.db.exists("Kuwaitisation Profile", company):
		frappe.get_doc({"doctype": "Kuwaitisation Profile", "company": company}).insert(ignore_permissions=True)
	profile = frappe.get_doc("Kuwaitisation Profile", company)

	target_percentage = get_applicable_target(company, profile.activity, profile.business_size)
	gap = round(kuwaiti_percentage - target_percentage, 2) if target_percentage is not None else 0.0

	profile.db_set(
		{
			"employee_count": counts["employee_count"],
			"kuwaiti_employee_count": counts["kuwaiti_employee_count"],
			"non_kuwaiti_employee_count": counts["non_kuwaiti_employee_count"],
			"kuwaiti_percentage": kuwaiti_percentage,
			"target_percentage": target_percentage or 0,
			"gap": gap,
			"compliance_status": compute_status(kuwaiti_percentage, target_percentage),
			"last_calculation": now_datetime(),
		},
		update_modified=False,
		notify=False,
	)
	profile.reload()
	return profile


def simulate(
	company: str,
	hire_kuwaiti: int = 0,
	hire_non_kuwaiti: int = 0,
	terminate_kuwaiti: int = 0,
	terminate_non_kuwaiti: int = 0,
) -> dict:
	"""Pure projection -- never writes to Employee/Kuwait Employee Profile."""
	counts = get_workforce_counts(company)
	profile = frappe.db.get_value("Kuwaitisation Profile", company, ["activity", "business_size"], as_dict=True) or {}

	projected_kuwaiti = max(0, counts["kuwaiti_employee_count"] + flt(hire_kuwaiti) - flt(terminate_kuwaiti))
	projected_non_kuwaiti = max(0, counts["non_kuwaiti_employee_count"] + flt(hire_non_kuwaiti) - flt(terminate_non_kuwaiti))
	projected_total = projected_kuwaiti + projected_non_kuwaiti

	projected_percentage = round(projected_kuwaiti / projected_total * 100, 2) if projected_total else 0.0
	target_percentage = get_applicable_target(company, profile.get("activity"), profile.get("business_size"))

	return {
		"current": counts,
		"current_percentage": round(
			counts["kuwaiti_employee_count"] / counts["employee_count"] * 100, 2
		)
		if counts["employee_count"]
		else 0.0,
		"projected_kuwaiti_employee_count": projected_kuwaiti,
		"projected_non_kuwaiti_employee_count": projected_non_kuwaiti,
		"projected_employee_count": projected_total,
		"projected_percentage": projected_percentage,
		"target_percentage": target_percentage,
		"projected_status": compute_status(projected_percentage, target_percentage),
	}
