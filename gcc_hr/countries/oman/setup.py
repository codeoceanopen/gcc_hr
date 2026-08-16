# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Oman's setup()/uninstall() -- dispatched by
gcc_hr_core/doctype/gcc_hr_company_settings/gcc_hr_company_settings.py's
run_country_setup() whenever a company's country is set to Oman, and by
gcc_hr/patches/v0_6/setup_oman.py for companies already pointed at Oman
before this module existed. Idempotent, mirrors countries/qatar/setup.py's
shape. Unlike UAE, Frappe HR ships no Oman regional package, so EOSB is
hand-rolled here, the same way Saudi's and Qatar's was."""

import frappe

DOCUMENT_TYPES = [
	"Resident Card",
	"Passport",
	"Work Permit",
	"Employment Contract",
	"National ID",
	"Health Certificate",
	"Professional License",
	"Driving License",
	"Visa",
	"Other",
]

COMPLIANCE_RULES = [
	{
		"rule_code": "OM_RESIDENT_CARD_EXPIRY",
		"rule_name": "Resident Card Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.oman.rules.check_resident_card_expiry",
	},
	{
		"rule_code": "OM_WORK_PERMIT_EXPIRY",
		"rule_name": "Work Permit Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.oman.rules.check_work_permit_expiry",
	},
	{
		"rule_code": "OM_PASSPORT_EXPIRY",
		"rule_name": "Passport Expiry",
		"category": "Document",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.oman.rules.check_passport_expiry",
	},
	{
		"rule_code": "OM_NON_OMANI_RESIDENT_CARD_ON_FILE",
		"rule_name": "Non-Omani Employee Has Resident Card On File",
		"category": "Employee",
		"severity": "Blocking",
		"check_method": "gcc_hr.countries.oman.rules.check_non_omani_has_resident_card",
	},
	{
		"rule_code": "OM_CONTRACT_ACTIVE",
		"rule_name": "Employment Contract Active",
		"category": "Contract",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.oman.rules.check_contract_active",
	},
	{
		"rule_code": "OM_CONTRACT_SALARY_MATCH",
		"rule_name": "Contract vs Payroll Salary Match",
		"category": "Payroll",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.oman.rules.check_contract_salary_match",
	},
	{
		"rule_code": "OM_PASI_REGISTERED",
		"rule_name": "PASI Registered",
		"category": "Payroll",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.oman.rules.check_pasi_registered",
	},
]

# Oman Labour Law (Royal Decree 35/2003, as amended), end-of-service
# gratuity for private-sector expatriate employees: 15 days' basic wage per
# year for each of the first three years, one month's wage per year after
# that. Modelled the same way Saudi's Phase 3 EOSB rule is: one Gratuity
# Rule, slabs expressed as a fraction of a 30-day month's wage per year of
# service. Illustrative starting point -- verify against current Ministry
# of Labour guidance; this app doesn't model any resignation-specific
# reduction for Oman, since that nuance isn't confidently sourced here (same
# caution Qatar's Phase 6 EOSB rule took).
GRATUITY_RULES = [
	{
		"name": "Oman - Standard EOSB (First 3 Years + Thereafter)",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 0,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 3, "fraction_of_applicable_earnings": 15 / 30},
			{"from_year": 3, "to_year": 0, "fraction_of_applicable_earnings": 1},
		],
	},
]

for _rule in GRATUITY_RULES:
	_rule["applicable_earnings_component"] = [{"salary_component": "Basic"}]

SEED_DESCRIPTION = (
	"Seeded illustrative starting value -- verify against current Ministry of Labour guidance "
	"before relying on this for real payroll."
)

# Omanisation is one of the oldest, most established GCC nationalization
# schemes (sector-specific Ministry of Labour quotas dating back decades),
# but the exact percentage still varies by sector/activity and changes by
# ministerial decision -- this single global-fallback row is a round,
# clearly-illustrative placeholder, not a claim of any real sector's
# requirement.
DEFAULT_OMANISATION_TARGET = 15.0

OMANISATION_SEED_DESCRIPTION = (
	"Seeded illustrative global fallback -- Omanisation's real required percentage varies by "
	"economic activity and establishment size. Add activity/business-size-specific rows (or a "
	"company-specific override) before relying on this for real compliance decisions, and verify "
	"against current Ministry of Labour guidance."
)

# Neither submission type calls, or pretends to call, a real government API
# (Oman's Ministry of Labour and PASI don't expose a verified public one
# for these) -- both just turn data this app already tracks into a document
# a human takes to the real portal.
GOVERNMENT_SUBMISSION_TYPES = [
	{
		"submission_type_code": "OM_OMANISATION_REPORT",
		"submission_type_name": "Omanisation Workforce Report",
		"category": "Workforce",
		"reference_doctype": "Omanisation Profile",
		"generate_method": "gcc_hr.countries.oman.government.generate_omanisation_report",
		"validate_method": "gcc_hr.countries.oman.government.validate_omanisation_report",
		"portal_url": "https://www.manpower.gov.om",
		"portal_instructions": (
			"Download the generated report and file it through the Ministry of Labour's Omanisation "
			"reporting workflow (the Ministry does not expose a verified public API for this)."
		),
	},
	{
		"submission_type_code": "OM_PASI_REGISTRATION",
		"submission_type_name": "PASI Registration Worksheet",
		"category": "Registration",
		"reference_doctype": "Oman Employee Profile",
		"generate_method": "gcc_hr.countries.oman.government.generate_pasi_registration_summary",
		"validate_method": "gcc_hr.countries.oman.government.validate_pasi_registration_summary",
		"portal_url": "https://www.pasi.gov.om",
		"portal_instructions": (
			"Use the worksheet to register each unregistered employee through PASI / the Social "
			"Protection Fund, then come back and mark this submission Submitted."
		),
	},
]


def setup(company=None):
	create_document_types()
	create_compliance_rules()
	create_gratuity_rules()
	create_omanisation_requirement()
	create_government_submission_types()
	frappe.db.set_value("HR Country Settings", "Oman", "compliance_engine_enabled", 1)
	if company:
		ensure_omanisation_profile(company)


def uninstall():
	frappe.db.set_value("HR Country Settings", "Oman", "compliance_engine_enabled", 0)


def create_document_types():
	for document_type_name in DOCUMENT_TYPES:
		name = f"Oman-{document_type_name}"
		if frappe.db.exists("HR Document Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "HR Document Type",
				"country": "Oman",
				"document_type_name": document_type_name,
				"requires_government_verification": document_type_name in ("Resident Card", "Work Permit", "Visa"),
			}
		).insert(ignore_permissions=True)


def create_compliance_rules():
	for rule in COMPLIANCE_RULES:
		if frappe.db.exists("HR Compliance Rule", rule["rule_code"]):
			continue
		frappe.get_doc({"doctype": "HR Compliance Rule", "country": "Oman", "enabled": 1, **rule}).insert(
			ignore_permissions=True
		)


def create_gratuity_rules():
	for rule in GRATUITY_RULES:
		if frappe.db.exists("Gratuity Rule", rule["name"]):
			continue
		frappe.get_doc({"doctype": "Gratuity Rule", **rule}).insert(ignore_permissions=True, ignore_if_duplicate=True)


def create_omanisation_requirement():
	if frappe.db.exists(
		"Omanisation Requirement",
		{"company": ["in", ("", None)], "activity": ["in", ("", None)], "effective_from": "2024-01-01"},
	):
		return
	frappe.get_doc(
		{
			"doctype": "Omanisation Requirement",
			# Explicit "" -- same default-injection footgun as
			# Saudization/Qatarization/Emiratisation Requirement.
			"company": "",
			"target_percentage": DEFAULT_OMANISATION_TARGET,
			"effective_from": "2024-01-01",
			"description": OMANISATION_SEED_DESCRIPTION,
		}
	).insert(ignore_permissions=True)


def ensure_omanisation_profile(company):
	from gcc_hr.countries.oman.omanisation import recalculate

	recalculate(company)


def create_government_submission_types():
	for submission_type in GOVERNMENT_SUBMISSION_TYPES:
		if frappe.db.exists("Government Submission Type", submission_type["submission_type_code"]):
			continue
		frappe.get_doc({"doctype": "Government Submission Type", "country": "Oman", "is_active": 1, **submission_type}).insert(
			ignore_permissions=True
		)
