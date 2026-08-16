# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Compliance scoring: weighted deduction -> score (0-100) -> status band.

Score bands are configured on `HR Compliance Score Band` (country specific,
or blank to apply globally). The defaults below mirror the brief (90-100
Excellent, 75-89 Compliant, 50-74 Warning, 0-49 Critical) and are only a
fallback used when no band rows have been configured yet.
"""

import frappe

SEVERITY_WEIGHT = {
	"Info": 2,
	"Warning": 8,
	"Critical": 20,
	"Blocking": 30,
}

DEFAULT_SCORE_BANDS = [
	{"min_score": 90, "max_score": 100, "compliance_status": "Compliant"},
	{"min_score": 75, "max_score": 89, "compliance_status": "Compliant"},
	{"min_score": 50, "max_score": 74, "compliance_status": "Warning"},
	{"min_score": 0, "max_score": 49, "compliance_status": "Critical"},
]


def calculate_score(failed_results: list[dict]) -> float:
	"""failed_results: list of {"severity": ...} for every Failed rule result."""
	score = 100.0
	for result in failed_results:
		score -= SEVERITY_WEIGHT.get(result.get("severity"), SEVERITY_WEIGHT["Warning"])
	return max(0.0, round(score, 1))


def get_status_for_score(score: float, country: str | None) -> str:
	rows = frappe.get_all(
		"HR Compliance Score Band",
		fields=["min_score", "max_score", "compliance_status", "country"],
	)
	matching = [r for r in rows if not r.country or r.country == country]
	bands = matching or DEFAULT_SCORE_BANDS
	for band in bands:
		if band["min_score"] <= score <= band["max_score"]:
			return band["compliance_status"]
	return "Critical"
