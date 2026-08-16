# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Command Center summary -- the one endpoint in Phase 1 that genuinely needs
server-side aggregation (group-by counts + an average) that a plain
frappe.client.get_list/get_count call from the frontend can't express in a
single round trip. Every other page in the SPA talks to frappe.client.*
directly via frappe-ui's createListResource/createDocumentResource.

The optional `company` filter (added for the Saudi Compliance Dashboard,
frontend/src/pages/saudi/ComplianceDashboard.vue) reuses the exact same
aggregation shape rather than adding a second, near-duplicate endpoint."""

import frappe
from frappe.utils import add_months, today


def _get_compliance_trend(company: str | None, months: int = 6) -> list[dict]:
	"""Real historical trend from HR Compliance Check.check_date/compliance_score
	(populated by every run_compliance_check call, including the daily
	scheduled sweep -- see compliance_engine/engine.py). Grouped by month via
	raw SQL since frappe.get_all's group_by can't date-truncate. Note:
	HR Compliance Check.company (fetch_from employee.company) is guaranteed
	populated; .country is NOT (see gcc_hr_company_settings research), so
	this deliberately filters by company, never country."""
	since = add_months(today(), -months)
	conditions = "check_date >= %(since)s"
	params = {"since": since}
	if company:
		conditions += " AND company = %(company)s"
		params["company"] = company

	rows = frappe.db.sql(
		f"""
		SELECT DATE_FORMAT(check_date, '%%Y-%%m') AS month, AVG(compliance_score) AS avg_score
		FROM `tabHR Compliance Check`
		WHERE {conditions}
		GROUP BY month
		ORDER BY month
		""",
		params,
		as_dict=True,
	)
	return [{"month": row.month, "average_score": round(float(row.avg_score or 0), 1)} for row in rows]


def _get_recent_critical_issues(company: str | None, limit: int = 8) -> list[dict]:
	"""Unified, real-data-only feed of the most urgent items across HR
	Compliance Document (expired/expiring) and Contract (past end_date) --
	no fabricated entries; an empty list means nothing urgent, not "no data
	yet". Contract has no `company` field directly (standard ERPNext CRM
	doctype, party_type=Employee) so company-scoping goes through Employee."""
	issues = []

	doc_filters: dict = {"status": ["in", ("Expired", "Expiring Soon")]}
	if company:
		doc_filters["company"] = company
	for row in frappe.get_all(
		"HR Compliance Document",
		filters=doc_filters,
		fields=["employee_name", "document_type", "status", "days_remaining", "expiry_date"],
		order_by="days_remaining asc",
		limit_page_length=limit,
	):
		if row.status == "Expired":
			label = f"{row.document_type} expired"
		else:
			label = f"{row.document_type} expires in {row.days_remaining} day(s)"
		issues.append(
			{
				"label": label,
				"reference": row.employee_name,
				"date": row.expiry_date,
				"severity": "danger" if row.status == "Expired" else "warning",
			}
		)

	contract_filters: dict = {"party_type": "Employee", "end_date": ["<", today()]}
	skip_contracts = False
	if company:
		employees = frappe.get_all("Employee", filters={"company": company}, pluck="name")
		if not employees:
			skip_contracts = True
		else:
			contract_filters["party_name"] = ["in", employees]
	if not skip_contracts:
		for row in frappe.get_all(
			"Contract",
			filters=contract_filters,
			fields=["party_name", "end_date"],
			order_by="end_date desc",
			limit_page_length=limit,
		):
			issues.append({"label": "Contract expired", "reference": row.party_name, "date": row.end_date, "severity": "danger"})

	issues.sort(key=lambda i: i["date"] or "", reverse=True)
	return issues[:limit]


@frappe.whitelist()
def get_summary(company: str | None = None, trend_months: int = 6):
	frappe.only_for(
		(
			"System Manager",
			"GCC HR Administrator",
			"HR Manager",
			"HR Officer",
			"Compliance Manager",
			"Compliance Officer",
			"Payroll Manager",
		),
		message=frappe._("Not permitted to view the GCC HR dashboard."),
	)

	profile_filters = {"company": company} if company else {}
	doc_filters = {"company": company} if company else {}

	status_counts = dict.fromkeys(("Compliant", "Warning", "Critical", "Blocked"), 0)
	for row in frappe.get_all(
		"Employee Compliance Profile",
		filters=profile_filters,
		group_by="compliance_status",
		fields=["compliance_status", {"COUNT": "*", "as": "count"}],
	):
		if row.compliance_status in status_counts:
			status_counts[row.compliance_status] = row.count

	total_employees = sum(status_counts.values())
	avg_score_row = frappe.get_all(
		"Employee Compliance Profile", filters=profile_filters, fields=[{"AVG": "compliance_score", "as": "avg_score"}]
	)
	avg_score = float((avg_score_row[0].avg_score if avg_score_row else None) or 0)

	doc_status_counts = dict.fromkeys(("Valid", "Expiring Soon", "Expired"), 0)
	for row in frappe.get_all(
		"HR Compliance Document", filters=doc_filters, group_by="status", fields=["status", {"COUNT": "*", "as": "count"}]
	):
		if row.status in doc_status_counts:
			doc_status_counts[row.status] = row.count

	documents_expiring_by_type = []
	if company:
		documents_expiring_by_type = frappe.get_all(
			"HR Compliance Document",
			filters={"company": company, "status": "Expiring Soon"},
			group_by="document_type",
			fields=["document_type", {"COUNT": "*", "as": "count"}],
			order_by="count desc",
		)

	return {
		"total_employees": total_employees,
		"status_counts": status_counts,
		"average_score": round(avg_score, 1),
		"documents_expiring_soon": doc_status_counts["Expiring Soon"],
		"documents_expired": doc_status_counts["Expired"],
		"documents_valid": doc_status_counts["Valid"],
		"documents_expiring_by_type": documents_expiring_by_type,
		"active_rules": frappe.db.count("HR Compliance Rule", {"enabled": 1}),
		"active_countries": frappe.db.count(
			"HR Country Settings", {"is_active": 1, "compliance_engine_enabled": 1}
		),
		"compliance_trend": _get_compliance_trend(company, months=int(trend_months or 6)),
		"recent_critical_issues": _get_recent_critical_issues(company),
	}
