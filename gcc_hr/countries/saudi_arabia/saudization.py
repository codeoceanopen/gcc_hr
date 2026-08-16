# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Saudization (Nitaqat) workforce-nationalization tracking. Target
percentages are never hard-coded -- see Saudization Requirement, matched by
company override, then Activity+Business Size, then a global fallback, all
effective-dated the same way GOSI Settings is (gosi_settings.py's
get_applicable_settings). The status-band tolerance (2 points) below is this
app's own UX threshold for "how close counts as at-risk", not a claim about
any official Nitaqat rule -- unlike the target percentage itself, which
always comes from Saudization Requirement.
"""

import frappe
from frappe.utils import flt, getdate, now_datetime, today

AT_RISK_TOLERANCE = 2.0


def get_applicable_target(company: str, activity: str | None, business_size: str | None, on_date=None) -> float | None:
	on_date = getdate(on_date or today())
	rows = frappe.get_all(
		"Saudization Requirement",
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
		return {"employee_count": 0, "saudi_employee_count": 0, "non_saudi_employee_count": 0}

	saudi_count = frappe.db.count(
		"Saudi Employee Profile", {"employee": ["in", employees], "nationality_status": "Saudi"}
	)
	non_saudi_count = frappe.db.count(
		"Saudi Employee Profile", {"employee": ["in", employees], "nationality_status": "Non-Saudi"}
	)
	return {
		"employee_count": len(employees),
		"saudi_employee_count": saudi_count,
		"non_saudi_employee_count": non_saudi_count,
	}


def compute_status(saudi_percentage: float, target_percentage: float | None) -> str:
	if target_percentage is None:
		return "Compliant"  # nothing configured to fall short of
	if saudi_percentage >= target_percentage:
		return "Compliant"
	if saudi_percentage >= target_percentage - AT_RISK_TOLERANCE:
		return "At Risk"
	return "Non-Compliant"


def recalculate(company: str):
	counts = get_workforce_counts(company)
	saudi_percentage = (
		round(counts["saudi_employee_count"] / counts["employee_count"] * 100, 2) if counts["employee_count"] else 0.0
	)

	if not frappe.db.exists("Saudization Profile", company):
		frappe.get_doc({"doctype": "Saudization Profile", "company": company}).insert(ignore_permissions=True)
	profile = frappe.get_doc("Saudization Profile", company)

	target_percentage = get_applicable_target(company, profile.activity, profile.business_size)
	gap = round(saudi_percentage - target_percentage, 2) if target_percentage is not None else 0.0

	profile.db_set(
		{
			"employee_count": counts["employee_count"],
			"saudi_employee_count": counts["saudi_employee_count"],
			"non_saudi_employee_count": counts["non_saudi_employee_count"],
			"saudi_percentage": saudi_percentage,
			"target_percentage": target_percentage or 0,
			"gap": gap,
			"compliance_status": compute_status(saudi_percentage, target_percentage),
			"last_calculation": now_datetime(),
		},
		update_modified=False,
		notify=False,
	)
	profile.reload()
	return profile


def simulate(
	company: str,
	hire_saudi: int = 0,
	hire_non_saudi: int = 0,
	terminate_saudi: int = 0,
	terminate_non_saudi: int = 0,
) -> dict:
	"""Pure projection -- never writes to Employee/Saudi Employee Profile."""
	counts = get_workforce_counts(company)
	profile = frappe.db.get_value("Saudization Profile", company, ["activity", "business_size"], as_dict=True) or {}

	projected_saudi = max(0, counts["saudi_employee_count"] + flt(hire_saudi) - flt(terminate_saudi))
	projected_non_saudi = max(0, counts["non_saudi_employee_count"] + flt(hire_non_saudi) - flt(terminate_non_saudi))
	projected_total = projected_saudi + projected_non_saudi

	projected_percentage = round(projected_saudi / projected_total * 100, 2) if projected_total else 0.0
	target_percentage = get_applicable_target(company, profile.get("activity"), profile.get("business_size"))

	return {
		"current": counts,
		"current_percentage": round(
			counts["saudi_employee_count"] / counts["employee_count"] * 100, 2
		)
		if counts["employee_count"]
		else 0.0,
		"projected_saudi_employee_count": projected_saudi,
		"projected_non_saudi_employee_count": projected_non_saudi,
		"projected_employee_count": projected_total,
		"projected_percentage": projected_percentage,
		"target_percentage": target_percentage,
		"projected_status": compute_status(projected_percentage, target_percentage),
	}
