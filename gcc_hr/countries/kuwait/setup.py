# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Kuwait's setup()/uninstall() -- dispatched by
gcc_hr_core/doctype/gcc_hr_company_settings/gcc_hr_company_settings.py's
run_country_setup() whenever a company's country is set to Kuwait, and by
gcc_hr/patches/v0_8/setup_kuwait.py for companies already pointed at Kuwait
before this module existed. Idempotent, mirrors countries/oman/setup.py's
shape for everything except GRATUITY_RULES, which mirrors Saudi Arabia's
multi-slab, resignation-reduction shape instead (Kuwait Labour Law No. 6 of
2010, Art. 51 uses the same day-fraction/resignation-band structure Saudi's
KSA Labour Law Art. 84 does)."""

import frappe

DOCUMENT_TYPES = [
	"Civil ID",
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
		"rule_code": "KWT_CIVIL_ID_EXPIRY",
		"rule_name": "Civil ID Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.kuwait.rules.check_civil_id_expiry",
	},
	{
		"rule_code": "KWT_WORK_PERMIT_EXPIRY",
		"rule_name": "Work Permit Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.kuwait.rules.check_work_permit_expiry",
	},
	{
		"rule_code": "KWT_PASSPORT_EXPIRY",
		"rule_name": "Passport Expiry",
		"category": "Document",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.kuwait.rules.check_passport_expiry",
	},
	{
		"rule_code": "KWT_NON_KUWAITI_CIVIL_ID_ON_FILE",
		"rule_name": "Non-Kuwaiti Employee Has Civil ID On File",
		"category": "Employee",
		"severity": "Blocking",
		"check_method": "gcc_hr.countries.kuwait.rules.check_non_kuwaiti_has_civil_id",
	},
	{
		"rule_code": "KWT_CONTRACT_ACTIVE",
		"rule_name": "Employment Contract Active",
		"category": "Contract",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.kuwait.rules.check_contract_active",
	},
	{
		"rule_code": "KWT_CONTRACT_SALARY_MATCH",
		"rule_name": "Contract vs Payroll Salary Match",
		"category": "Payroll",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.kuwait.rules.check_contract_salary_match",
	},
	{
		"rule_code": "KWT_WPS_REGISTERED",
		"rule_name": "WPS Registered",
		"category": "Payroll",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.kuwait.rules.check_wps_registered",
	},
]

# Kuwait Labour Law No. 6 of 2010, Article 51: 15 days' wage per year of
# service for each of the first five years, one month's wage per year of
# service after that -- identical day-fractions to Saudi's KSA Labour Law
# Art. 84 rule. On resignation, the award is commonly cited as reduced the
# same way Saudi's is: none under 2 years, 1/3 from 2-5 years, 2/3 from
# 5-10 years, full at 10+ years. Modelled the same way
# countries/saudi_arabia/setup.py models Saudi's equivalent: one Gratuity
# Rule per HR-selected scenario, slabs expressed as a fraction of a 30-day
# month's wage per year of service. Illustrative starting point -- verify
# against current Public Authority for Manpower guidance before relying on
# this for real payroll.
GRATUITY_RULES = [
	{
		"name": "Kuwait - Full Award (Termination/Retirement/Contract End)",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 0,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 5, "fraction_of_applicable_earnings": 15 / 30},
			{"from_year": 5, "to_year": 0, "fraction_of_applicable_earnings": 1},
		],
	},
	{
		"name": "Kuwait - Resignation 2-5 Years (1/3 Award)",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 2,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 5, "fraction_of_applicable_earnings": (15 / 30) * (1 / 3)},
		],
	},
	{
		"name": "Kuwait - Resignation 5-10 Years (2/3 Award)",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 5,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 5, "fraction_of_applicable_earnings": (15 / 30) * (2 / 3)},
			{"from_year": 5, "to_year": 10, "fraction_of_applicable_earnings": 1 * (2 / 3)},
		],
	},
	{
		"name": "Kuwait - Resignation 10+ Years (Full Award)",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 10,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 5, "fraction_of_applicable_earnings": 15 / 30},
			{"from_year": 5, "to_year": 0, "fraction_of_applicable_earnings": 1},
		],
	},
]

for _rule in GRATUITY_RULES:
	# Gratuity's own applicable_earnings_component is mandatory; base the
	# award on Basic salary, same component Saudi's own seeded rules imply.
	_rule["applicable_earnings_component"] = [{"salary_component": "Basic"}]

SEED_DESCRIPTION = (
	"Seeded illustrative starting value -- verify against current Public Authority for Manpower "
	"guidance before relying on this for real payroll."
)

# Kuwaitisation's actual required percentage varies by sector/activity and
# changes by administrative decision, the same general shape as
# Omanisation/Bahrainisation/Emiratisation/Qatarization -- this single
# global-fallback row is a round, clearly-illustrative placeholder, not a
# claim of any real sector's requirement. See Kuwaitisation
# Requirement.description on the seeded row, and add real activity/size-
# specific rows before relying on this for workforce-planning decisions.
DEFAULT_KUWAITISATION_TARGET = 20.0

KUWAITISATION_SEED_DESCRIPTION = (
	"Seeded illustrative global fallback -- Kuwaitisation's real required percentage varies by "
	"economic activity and establishment size. Add activity/business-size-specific rows (or a "
	"company-specific override) before relying on this for real compliance decisions, and verify "
	"against current Public Authority for Manpower guidance."
)

# Neither submission type calls, or pretends to call, a real government API
# (Kuwait's Public Authority for Manpower doesn't expose a verified public
# one for these) -- both just turn data this app already tracks into a
# document a human takes to the real portal.
GOVERNMENT_SUBMISSION_TYPES = [
	{
		"submission_type_code": "KWT_KUWAITISATION_REPORT",
		"submission_type_name": "Kuwaitisation Workforce Report",
		"category": "Workforce",
		"reference_doctype": "Kuwaitisation Profile",
		"generate_method": "gcc_hr.countries.kuwait.government.generate_kuwaitisation_report",
		"validate_method": "gcc_hr.countries.kuwait.government.validate_kuwaitisation_report",
		"portal_url": "https://www.papam.gov.kw",
		"portal_instructions": (
			"Download the generated report and file it through the Public Authority for Manpower's "
			"Kuwaitisation reporting workflow (the Authority does not expose a verified public API "
			"for this)."
		),
	},
	{
		"submission_type_code": "KWT_WPS_REPORT",
		"submission_type_name": "WPS Registration Worksheet",
		"category": "Registration",
		"reference_doctype": "Kuwait Employee Profile",
		"generate_method": "gcc_hr.countries.kuwait.government.generate_wps_report",
		"validate_method": "gcc_hr.countries.kuwait.government.validate_wps_report",
		"portal_url": "https://www.papam.gov.kw",
		"portal_instructions": (
			"Use the worksheet to register each unregistered employee's salary payment through the "
			"Wage Protection System, then come back and mark this submission Submitted."
		),
	},
]


def setup(company=None):
	create_document_types()
	create_compliance_rules()
	create_gratuity_rules()
	create_kuwaitisation_requirement()
	create_government_submission_types()
	frappe.db.set_value("HR Country Settings", "Kuwait", "compliance_engine_enabled", 1)
	if company:
		ensure_kuwaitisation_profile(company)


def uninstall():
	frappe.db.set_value("HR Country Settings", "Kuwait", "compliance_engine_enabled", 0)


def create_document_types():
	for document_type_name in DOCUMENT_TYPES:
		name = f"Kuwait-{document_type_name}"
		if frappe.db.exists("HR Document Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "HR Document Type",
				"country": "Kuwait",
				"document_type_name": document_type_name,
				"requires_government_verification": document_type_name in ("Civil ID", "Work Permit", "Visa"),
			}
		).insert(ignore_permissions=True)


def create_compliance_rules():
	for rule in COMPLIANCE_RULES:
		if frappe.db.exists("HR Compliance Rule", rule["rule_code"]):
			continue
		frappe.get_doc({"doctype": "HR Compliance Rule", "country": "Kuwait", "enabled": 1, **rule}).insert(
			ignore_permissions=True
		)


def create_gratuity_rules():
	for rule in GRATUITY_RULES:
		if frappe.db.exists("Gratuity Rule", rule["name"]):
			continue
		frappe.get_doc({"doctype": "Gratuity Rule", **rule}).insert(ignore_permissions=True, ignore_if_duplicate=True)


def create_kuwaitisation_requirement():
	if frappe.db.exists(
		"Kuwaitisation Requirement",
		{"company": ["in", ("", None)], "activity": ["in", ("", None)], "effective_from": "2024-01-01"},
	):
		return
	frappe.get_doc(
		{
			"doctype": "Kuwaitisation Requirement",
			# Explicit "" -- same default-injection footgun as
			# Saudization/Qatarization/Emiratisation/Omanisation Requirement.
			"company": "",
			"target_percentage": DEFAULT_KUWAITISATION_TARGET,
			"effective_from": "2024-01-01",
			"description": KUWAITISATION_SEED_DESCRIPTION,
		}
	).insert(ignore_permissions=True)


def ensure_kuwaitisation_profile(company):
	from gcc_hr.countries.kuwait.kuwaitisation import recalculate

	recalculate(company)


def create_government_submission_types():
	for submission_type in GOVERNMENT_SUBMISSION_TYPES:
		if frappe.db.exists("Government Submission Type", submission_type["submission_type_code"]):
			continue
		frappe.get_doc({"doctype": "Government Submission Type", "country": "Kuwait", "is_active": 1, **submission_type}).insert(
			ignore_permissions=True
		)
