# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Rule-driven compliance engine.

Which rules run, their severity and effective dates are configuration
(`HR Compliance Rule`). The predicate for each rule is still a Python
callable (`check_method`) -- see that doctype's docstring -- because "is this
Iqama expiring" genuinely needs code, but nothing about *which* rules apply,
*when*, or how *severe* a failure is, is hard-coded here.
"""

import frappe
from frappe.utils import add_days, getdate, now_datetime, today

from gcc_hr.gcc_hr_core.compliance_engine.scoring import calculate_score, get_status_for_score


def get_active_rules(country: str) -> list[dict]:
	rules = frappe.get_all(
		"HR Compliance Rule",
		filters={"country": country, "enabled": 1},
		fields=["name", "rule_code", "category", "severity", "check_method", "effective_from", "effective_to"],
	)
	current = getdate(today())
	return [
		r
		for r in rules
		if (not r.effective_from or getdate(r.effective_from) <= current)
		and (not r.effective_to or getdate(r.effective_to) >= current)
	]


def run_compliance_check(employee: str, reason: str = "Scheduled") -> "frappe.model.document.Document | None":
	if not frappe.db.exists("Employee Compliance Profile", employee):
		return None

	profile = frappe.get_doc("Employee Compliance Profile", employee)
	country = profile.country
	if not country:
		return None

	rules = get_active_rules(country)
	results, failed_for_scoring = [], []
	passed = warnings = critical = 0

	for rule in rules:
		result, message, action = _evaluate_rule(employee, profile, rule)
		results.append(
			{
				"rule": rule.name,
				"category": rule.category,
				"result": result,
				"severity": rule.severity,
				"message": message,
				"recommended_action": action,
			}
		)
		if result == "Passed":
			passed += 1
		elif result == "Failed":
			failed_for_scoring.append({"severity": rule.severity})
			if rule.severity in ("Critical", "Blocking"):
				critical += 1
			elif rule.severity == "Warning":
				warnings += 1

	score = calculate_score(failed_for_scoring)
	status = get_status_for_score(score, country)

	check = frappe.get_doc(
		{
			"doctype": "HR Compliance Check",
			"employee": employee,
			"compliance_score": score,
			"status": status,
			"passed_rules": passed,
			"warnings": warnings,
			"critical_issues": critical,
			"results": results,
		}
	)
	check.insert(ignore_permissions=True)

	profile.db_set(
		{
			"compliance_score": score,
			"compliance_status": status,
			"last_compliance_check": now_datetime(),
			"next_compliance_check": add_days(today(), 1),
		},
		update_modified=False,
		notify=False,
	)

	from gcc_hr.gcc_hr_core.audit import log_action

	log_action(
		action="Compliance Check",
		reference_doctype="HR Compliance Check",
		reference_name=check.name,
		employee=employee,
		company=profile.company,
		new_value=f"score={score} status={status}",
		reason=reason,
		source="Scheduled Job" if reason == "Scheduled" else "System",
	)

	return check


def _evaluate_rule(employee: str, profile, rule: dict) -> tuple[str, str, str]:
	try:
		func = frappe.get_attr(rule.check_method)
	except Exception:
		frappe.log_error(title="GCC HR: invalid compliance rule check_method", message=frappe.get_traceback())
		return "Skipped", f"Check Method {rule.check_method} could not be imported.", ""

	try:
		result, message, action = func(employee=employee, profile=profile, rule=rule)
	except Exception:
		frappe.log_error(title="GCC HR: compliance rule evaluation failed", message=frappe.get_traceback())
		return "Skipped", f"{rule.rule_code} raised an error during evaluation.", ""

	if result not in ("Passed", "Failed", "Skipped"):
		return "Skipped", f"{rule.rule_code} returned an invalid result: {result}", ""

	return result, message or "", action or ""


def run_daily_compliance_sweep():
	"""scheduler_events.daily -- recompute compliance for every employee whose
	country has the compliance engine enabled."""
	countries = frappe.get_all(
		"HR Country Settings", filters={"is_active": 1, "compliance_engine_enabled": 1}, pluck="name"
	)
	if not countries:
		return

	employees = frappe.get_all(
		"Employee Compliance Profile", filters={"country": ["in", countries]}, pluck="employee"
	)
	for employee in employees:
		run_compliance_check(employee, reason="Scheduled")
	frappe.db.commit()
