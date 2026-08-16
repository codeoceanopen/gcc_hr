# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Document expiry status engine.

Thresholds are configured on `HR Document Expiry Threshold` (country / document
type specific, or blank to apply globally). The defaults below (mirroring the
brief: 90/60/30/14/7/0 days) are only a fallback used when no threshold rows
have been configured yet -- see gcc_hr/fixtures for the seeded defaults.
"""

import frappe
from frappe.utils import getdate, today

DEFAULT_THRESHOLDS = [
	{"threshold_days": 90, "severity": "Info"},
	{"threshold_days": 60, "severity": "Info"},
	{"threshold_days": 30, "severity": "Warning"},
	{"threshold_days": 14, "severity": "Warning"},
	{"threshold_days": 7, "severity": "Critical"},
	{"threshold_days": 0, "severity": "Blocking"},
]


def get_applicable_thresholds(country: str | None, document_type: str | None) -> list[dict]:
	rows = frappe.get_all(
		"HR Document Expiry Threshold",
		filters={"is_active": 1},
		fields=["label", "threshold_days", "severity", "country", "document_type"],
	)
	matching = [
		r
		for r in rows
		if (not r.country or r.country == country) and (not r.document_type or r.document_type == document_type)
	]
	return matching or DEFAULT_THRESHOLDS


def compute_status_for_document(
	expiry_date, country: str | None = None, document_type: str | None = None
) -> tuple[str, int, str]:
	"""Return (status, days_remaining, severity) for a document's expiry_date."""
	days_remaining = (getdate(expiry_date) - getdate(today())).days
	thresholds = sorted(get_applicable_thresholds(country, document_type), key=lambda r: r["threshold_days"])

	severity = "Info"
	for t in thresholds:
		if days_remaining <= t["threshold_days"]:
			severity = t["severity"]
			break  # thresholds are sorted ascending -- first match is the most urgent applicable one

	if days_remaining <= 0:
		status = "Expired"
	elif days_remaining <= max(t["threshold_days"] for t in thresholds):
		status = "Expiring Soon"
	else:
		status = "Valid"

	return status, days_remaining, severity


def run_daily_expiry_sweep():
	"""scheduler_events.daily -- recompute status/days_remaining on every open
	compliance document whose expiry_date is set. Changed documents are saved
	through the document lifecycle (not frappe.db.set_value) so that the
	fixture `Notification` records (Days Before / Value Change triggers on
	HR Compliance Document) still fire.
	"""
	documents = frappe.get_all(
		"HR Compliance Document",
		filters={"expiry_date": ["is", "set"]},
		fields=["name", "expiry_date", "country", "document_type", "status", "days_remaining"],
	)
	for row in documents:
		status, days_remaining, _severity = compute_status_for_document(
			expiry_date=row.expiry_date, country=row.country, document_type=row.document_type
		)
		if status != row.status or days_remaining != row.days_remaining:
			doc = frappe.get_doc("HR Compliance Document", row.name)
			doc.save(ignore_permissions=True)
	frappe.db.commit()
