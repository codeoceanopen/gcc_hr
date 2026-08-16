# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Qatarization workforce-nationalization tracking. Mirrors
countries/saudi_arabia/saudization.py's shape exactly (target lookup by
specificity, active-employee counts, risk band, pure what-if simulator) --
Qatar just doesn't have as uniformly codified a public quota system as
Saudi's Nitaqat, so Qatarization Requirement's seeded row is even more
explicitly an illustrative placeholder than Saudization Requirement's; see
that doctype's own description field."""

import frappe
from frappe.utils import flt, getdate, now_datetime, today

AT_RISK_TOLERANCE = 2.0


def get_applicable_target(company: str, activity: str | None, business_size: str | None, on_date=None) -> float | None:
	on_date = getdate(on_date or today())
	rows = frappe.get_all(
		"Qatarization Requirement",
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
		return {"employee_count": 0, "qatari_employee_count": 0, "non_qatari_employee_count": 0}

	qatari_count = frappe.db.count(
		"Qatar Employee Profile", {"employee": ["in", employees], "nationality_status": "Qatari"}
	)
	non_qatari_count = frappe.db.count(
		"Qatar Employee Profile", {"employee": ["in", employees], "nationality_status": "Non-Qatari"}
	)
	return {
		"employee_count": len(employees),
		"qatari_employee_count": qatari_count,
		"non_qatari_employee_count": non_qatari_count,
	}


def compute_status(qatari_percentage: float, target_percentage: float | None) -> str:
	if target_percentage is None:
		return "Compliant"  # nothing configured to fall short of
	if qatari_percentage >= target_percentage:
		return "Compliant"
	if qatari_percentage >= target_percentage - AT_RISK_TOLERANCE:
		return "At Risk"
	return "Non-Compliant"


def recalculate(company: str):
	counts = get_workforce_counts(company)
	qatari_percentage = (
		round(counts["qatari_employee_count"] / counts["employee_count"] * 100, 2) if counts["employee_count"] else 0.0
	)

	if not frappe.db.exists("Qatarization Profile", company):
		frappe.get_doc({"doctype": "Qatarization Profile", "company": company}).insert(ignore_permissions=True)
	profile = frappe.get_doc("Qatarization Profile", company)

	target_percentage = get_applicable_target(company, profile.activity, profile.business_size)
	gap = round(qatari_percentage - target_percentage, 2) if target_percentage is not None else 0.0

	profile.db_set(
		{
			"employee_count": counts["employee_count"],
			"qatari_employee_count": counts["qatari_employee_count"],
			"non_qatari_employee_count": counts["non_qatari_employee_count"],
			"qatari_percentage": qatari_percentage,
			"target_percentage": target_percentage or 0,
			"gap": gap,
			"compliance_status": compute_status(qatari_percentage, target_percentage),
			"last_calculation": now_datetime(),
		},
		update_modified=False,
		notify=False,
	)
	profile.reload()
	return profile


def simulate(
	company: str,
	hire_qatari: int = 0,
	hire_non_qatari: int = 0,
	terminate_qatari: int = 0,
	terminate_non_qatari: int = 0,
) -> dict:
	"""Pure projection -- never writes to Employee/Qatar Employee Profile."""
	counts = get_workforce_counts(company)
	profile = frappe.db.get_value("Qatarization Profile", company, ["activity", "business_size"], as_dict=True) or {}

	projected_qatari = max(0, counts["qatari_employee_count"] + flt(hire_qatari) - flt(terminate_qatari))
	projected_non_qatari = max(0, counts["non_qatari_employee_count"] + flt(hire_non_qatari) - flt(terminate_non_qatari))
	projected_total = projected_qatari + projected_non_qatari

	projected_percentage = round(projected_qatari / projected_total * 100, 2) if projected_total else 0.0
	target_percentage = get_applicable_target(company, profile.get("activity"), profile.get("business_size"))

	return {
		"current": counts,
		"current_percentage": round(
			counts["qatari_employee_count"] / counts["employee_count"] * 100, 2
		)
		if counts["employee_count"]
		else 0.0,
		"projected_qatari_employee_count": projected_qatari,
		"projected_non_qatari_employee_count": projected_non_qatari,
		"projected_employee_count": projected_total,
		"projected_percentage": projected_percentage,
		"target_percentage": target_percentage,
		"projected_status": compute_status(projected_percentage, target_percentage),
	}
