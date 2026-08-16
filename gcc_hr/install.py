# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""after_install seed data.

Unlike fixtures/ (which are re-synced -- and any local edits overwritten --
on every `bench migrate`), the records here are genuinely user-editable
settings (is_active, compliance_engine_enabled, threshold days, score
bands), so they're inserted once, idempotently, and never touched again by
this module.
"""

import frappe

GCC_COUNTRIES = [
	{"country": "Saudi Arabia", "currency": "SAR", "language": "ar", "timezone": "Asia/Riyadh"},
	{"country": "Qatar", "currency": "QAR", "language": "ar", "timezone": "Asia/Qatar"},
	{"country": "United Arab Emirates", "currency": "AED", "language": "ar", "timezone": "Asia/Dubai"},
	{"country": "Oman", "currency": "OMR", "language": "ar", "timezone": "Asia/Muscat"},
	{"country": "Bahrain", "currency": "BHD", "language": "ar", "timezone": "Asia/Bahrain"},
	{"country": "Kuwait", "currency": "KWD", "language": "ar", "timezone": "Asia/Kuwait"},
]

DEFAULT_THRESHOLDS = [
	{"label": "Expiring Soon", "threshold_days": 90, "severity": "Info"},
	{"label": "Expiring Soon", "threshold_days": 60, "severity": "Info"},
	{"label": "Expiring Soon", "threshold_days": 30, "severity": "Warning"},
	{"label": "Expiring Soon", "threshold_days": 14, "severity": "Warning"},
	{"label": "Critical", "threshold_days": 7, "severity": "Critical"},
	{"label": "Expired", "threshold_days": 0, "severity": "Blocking"},
]

DEFAULT_SCORE_BANDS = [
	{"status_label": "Excellent", "min_score": 90, "max_score": 100, "compliance_status": "Compliant", "color": "#29a568"},
	{"status_label": "Compliant", "min_score": 75, "max_score": 89, "compliance_status": "Compliant", "color": "#98d85b"},
	{"status_label": "Warning", "min_score": 50, "max_score": 74, "compliance_status": "Warning", "color": "#ffa00a"},
	{"status_label": "Critical", "min_score": 0, "max_score": 49, "compliance_status": "Critical", "color": "#e24c4c"},
]


def after_install():
	create_gcc_countries()
	create_default_expiry_thresholds()
	create_default_score_bands()


def create_gcc_countries():
	# Only Saudi Arabia's compliance engine is enabled -- Phase 1 ships the
	# country-agnostic foundation; Phase 2 seeds Saudi's document types and
	# compliance rules and flips compliance_engine_enabled on for it.
	for country in GCC_COUNTRIES:
		if frappe.db.exists("HR Country Settings", country["country"]):
			continue
		frappe.get_doc(
			{
				"doctype": "HR Country Settings",
				"is_active": 1,
				"compliance_engine_enabled": 0,
				"government_integration_enabled": 0,
				**country,
			}
		).insert(ignore_permissions=True)


def create_default_expiry_thresholds():
	if frappe.db.exists("HR Document Expiry Threshold"):
		return
	for threshold in DEFAULT_THRESHOLDS:
		frappe.get_doc({"doctype": "HR Document Expiry Threshold", "is_active": 1, **threshold}).insert(
			ignore_permissions=True
		)


def create_default_score_bands():
	if frappe.db.exists("HR Compliance Score Band"):
		return
	for band in DEFAULT_SCORE_BANDS:
		frappe.get_doc({"doctype": "HR Compliance Score Band", **band}).insert(ignore_permissions=True)
