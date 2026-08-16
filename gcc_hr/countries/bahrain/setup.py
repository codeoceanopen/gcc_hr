# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Bahrain's setup()/uninstall() -- dispatched by
gcc_hr_core/doctype/gcc_hr_company_settings/gcc_hr_company_settings.py's
run_country_setup() whenever a company's country is set to Bahrain, and by
gcc_hr/patches/v0_7/setup_bahrain.py for companies already pointed at
Bahrain before this module existed. Idempotent, mirrors
countries/oman/setup.py's shape. Frappe HR ships no Bahrain regional
package, so EOSB is hand-rolled here, the same way Saudi's, Qatar's, and
Oman's were."""

import frappe

DOCUMENT_TYPES = [
	"CPR",
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
		"rule_code": "BAH_CPR_EXPIRY",
		"rule_name": "CPR Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.bahrain.rules.check_cpr_expiry",
	},
	{
		"rule_code": "BAH_WORK_PERMIT_EXPIRY",
		"rule_name": "Work Permit Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.bahrain.rules.check_work_permit_expiry",
	},
	{
		"rule_code": "BAH_PASSPORT_EXPIRY",
		"rule_name": "Passport Expiry",
		"category": "Document",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.bahrain.rules.check_passport_expiry",
	},
	{
		"rule_code": "BAH_NON_BAHRAINI_CPR_ON_FILE",
		"rule_name": "Non-Bahraini Employee Has CPR On File",
		"category": "Employee",
		"severity": "Blocking",
		"check_method": "gcc_hr.countries.bahrain.rules.check_non_bahraini_has_cpr",
	},
	{
		"rule_code": "BAH_CONTRACT_ACTIVE",
		"rule_name": "Employment Contract Active",
		"category": "Contract",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.bahrain.rules.check_contract_active",
	},
	{
		"rule_code": "BAH_CONTRACT_SALARY_MATCH",
		"rule_name": "Contract vs Payroll Salary Match",
		"category": "Payroll",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.bahrain.rules.check_contract_salary_match",
	},
	{
		"rule_code": "BAH_SIO_REGISTERED",
		"rule_name": "SIO Registered",
		"category": "Payroll",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.bahrain.rules.check_sio_registered",
	},
]

# Bahrain Labour Law (Law No. 36 of 2012), Article 116, end-of-service
# gratuity for private-sector employees: half a month's wage for each of
# the first three years of service, one month's wage for each year after
# that. Modelled the same way Oman's Phase 8 EOSB rule is: one Gratuity
# Rule, slabs expressed as a fraction of a 30-day month's wage per year of
# service -- half a month is 15/30 of that, which happens to make Bahrain's
# two slabs numerically identical to Oman's (15 days for each of the first
# three years, one month per year after that), even though the two laws are
# independent. Illustrative starting point -- verify against current
# Ministry of Labour/LMRA guidance; this app doesn't model any
# resignation-specific reduction for Bahrain, since that nuance isn't
# confidently sourced here (same caution Qatar's and Oman's EOSB rules
# took).
GRATUITY_RULES = [
	{
		"name": "Bahrain - Standard EOSB (First 3 Years + Thereafter)",
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

# Bahrainisation is a real, established Ministry of Labour/Labour Market
# Regulatory Authority (LMRA) sector-specific quota scheme, but the exact
# percentage still varies by sector/activity and changes by ministerial
# decision -- this single global-fallback row is a round,
# clearly-illustrative placeholder, not a claim of any real sector's
# requirement.
DEFAULT_BAHRAINISATION_TARGET = 20.0

BAHRAINISATION_SEED_DESCRIPTION = (
	"Seeded illustrative global fallback -- Bahrainisation's real required percentage varies by "
	"economic activity and establishment size. Add activity/business-size-specific rows (or a "
	"company-specific override) before relying on this for real compliance decisions, and verify "
	"against current LMRA/Ministry of Labour guidance."
)

# Neither submission type calls, or pretends to call, a real government API
# (Bahrain's LMRA and SIO don't expose a verified public one for these) --
# both just turn data this app already tracks into a document a human takes
# to the real portal.
GOVERNMENT_SUBMISSION_TYPES = [
	{
		"submission_type_code": "BAH_BAHRAINISATION_REPORT",
		"submission_type_name": "Bahrainisation Workforce Report",
		"category": "Workforce",
		"reference_doctype": "Bahrainisation Profile",
		"generate_method": "gcc_hr.countries.bahrain.government.generate_bahrainisation_report",
		"validate_method": "gcc_hr.countries.bahrain.government.validate_bahrainisation_report",
		"portal_url": "https://www.lmra.bh",
		"portal_instructions": (
			"Download the generated report and file it through the Labour Market Regulatory "
			"Authority's (LMRA) Bahrainisation reporting workflow (the LMRA does not expose a "
			"verified public API for this)."
		),
	},
	{
		"submission_type_code": "BAH_SIO_REGISTRATION",
		"submission_type_name": "SIO Registration Worksheet",
		"category": "Registration",
		"reference_doctype": "Bahrain Employee Profile",
		"generate_method": "gcc_hr.countries.bahrain.government.generate_sio_registration_summary",
		"validate_method": "gcc_hr.countries.bahrain.government.validate_sio_registration_summary",
		"portal_url": "https://www.sio.gov.bh",
		"portal_instructions": (
			"Use the worksheet to register each unregistered employee through the Social Insurance "
			"Organisation (SIO), then come back and mark this submission Submitted."
		),
	},
]


def setup(company=None):
	create_document_types()
	create_compliance_rules()
	create_gratuity_rules()
	create_bahrainisation_requirement()
	create_government_submission_types()
	frappe.db.set_value("HR Country Settings", "Bahrain", "compliance_engine_enabled", 1)
	if company:
		ensure_bahrainisation_profile(company)


def uninstall():
	frappe.db.set_value("HR Country Settings", "Bahrain", "compliance_engine_enabled", 0)


def create_document_types():
	for document_type_name in DOCUMENT_TYPES:
		name = f"Bahrain-{document_type_name}"
		if frappe.db.exists("HR Document Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "HR Document Type",
				"country": "Bahrain",
				"document_type_name": document_type_name,
				"requires_government_verification": document_type_name in ("CPR", "Work Permit", "Visa"),
			}
		).insert(ignore_permissions=True)


def create_compliance_rules():
	for rule in COMPLIANCE_RULES:
		if frappe.db.exists("HR Compliance Rule", rule["rule_code"]):
			continue
		frappe.get_doc({"doctype": "HR Compliance Rule", "country": "Bahrain", "enabled": 1, **rule}).insert(
			ignore_permissions=True
		)


def create_gratuity_rules():
	for rule in GRATUITY_RULES:
		if frappe.db.exists("Gratuity Rule", rule["name"]):
			continue
		frappe.get_doc({"doctype": "Gratuity Rule", **rule}).insert(ignore_permissions=True, ignore_if_duplicate=True)


def create_bahrainisation_requirement():
	if frappe.db.exists(
		"Bahrainisation Requirement",
		{"company": ["in", ("", None)], "activity": ["in", ("", None)], "effective_from": "2024-01-01"},
	):
		return
	frappe.get_doc(
		{
			"doctype": "Bahrainisation Requirement",
			# Explicit "" -- same default-injection footgun as
			# Saudization/Qatarization/Emiratisation/Omanisation Requirement.
			"company": "",
			"target_percentage": DEFAULT_BAHRAINISATION_TARGET,
			"effective_from": "2024-01-01",
			"description": BAHRAINISATION_SEED_DESCRIPTION,
		}
	).insert(ignore_permissions=True)


def ensure_bahrainisation_profile(company):
	from gcc_hr.countries.bahrain.bahrainisation import recalculate

	recalculate(company)


def create_government_submission_types():
	for submission_type in GOVERNMENT_SUBMISSION_TYPES:
		if frappe.db.exists("Government Submission Type", submission_type["submission_type_code"]):
			continue
		frappe.get_doc({"doctype": "Government Submission Type", "country": "Bahrain", "is_active": 1, **submission_type}).insert(
			ignore_permissions=True
		)
