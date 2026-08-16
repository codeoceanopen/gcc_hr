# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Qatar's setup()/uninstall() -- dispatched by
gcc_hr_core/doctype/gcc_hr_company_settings/gcc_hr_company_settings.py's
run_country_setup() whenever a company's country is set to Qatar, and by
gcc_hr/patches/v0_4/setup_qatar.py for companies already pointed at Qatar
before this module existed. Idempotent, mirrors
countries/saudi_arabia/setup.py's shape."""

import frappe

DOCUMENT_TYPES = [
	"QID",
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
		"rule_code": "QAT_QID_EXPIRY",
		"rule_name": "QID Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.qatar.rules.check_qid_expiry",
	},
	{
		"rule_code": "QAT_WORK_PERMIT_EXPIRY",
		"rule_name": "Work Permit Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.qatar.rules.check_work_permit_expiry",
	},
	{
		"rule_code": "QAT_PASSPORT_EXPIRY",
		"rule_name": "Passport Expiry",
		"category": "Document",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.qatar.rules.check_passport_expiry",
	},
	{
		"rule_code": "QAT_NON_QATARI_QID_ON_FILE",
		"rule_name": "Non-Qatari Employee Has QID On File",
		"category": "Employee",
		"severity": "Blocking",
		"check_method": "gcc_hr.countries.qatar.rules.check_non_qatari_has_qid",
	},
	{
		"rule_code": "QAT_CONTRACT_ACTIVE",
		"rule_name": "Employment Contract Active",
		"category": "Contract",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.qatar.rules.check_contract_active",
	},
	{
		"rule_code": "QAT_CONTRACT_SALARY_MATCH",
		"rule_name": "Contract vs Payroll Salary Match",
		"category": "Payroll",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.qatar.rules.check_contract_salary_match",
	},
	{
		"rule_code": "QAT_WPS_REGISTERED",
		"rule_name": "WPS Registered",
		"category": "Payroll",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.qatar.rules.check_wps_registered",
	},
]

# Qatar Labour Law No. 14 of 2004, Art. 54: end-of-service gratuity of at
# least three weeks' basic wage per year of service, for employees who
# complete one year or more of service. Unlike Saudi's tiered
# resignation-vs-termination bands (Phase 3), this app only models the
# single standard/full-service rate -- any resignation-specific reduction
# under current law/MOL guidance is NOT modelled here; verify with current
# legal counsel before relying on this for a resignation case specifically.
GRATUITY_RULES = [
	{
		"name": "Qatar - Standard End of Service Gratuity",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 1,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 0, "fraction_of_applicable_earnings": 21 / 30},
		],
	},
]

for _rule in GRATUITY_RULES:
	_rule["applicable_earnings_component"] = [{"salary_component": "Basic"}]

# Qatar doesn't have as uniformly codified a public workforce-nationalization
# quota system as Saudi's Nitaqat -- this seeded row is an illustrative
# placeholder only, more explicitly so than Saudization's own seed. See
# Qatarization Requirement.description on the seeded row.
DEFAULT_QATARIZATION_TARGET = 15.0

QATARIZATION_SEED_DESCRIPTION = (
	"Seeded illustrative global fallback -- Qatarization targets are policy intent, not as "
	"uniformly codified in public quota bands as Saudi's Nitaqat. Add activity/business-size-"
	"specific rows (or a company-specific override) before relying on this for real compliance "
	"decisions, and verify against current MOL/ADLSA guidance."
)

# Neither submission type calls, or pretends to call, a real government API
# (Qatar's MOL and QCB don't expose a verified public one for these) -- both
# just turn data this app already tracks into a document a human takes to
# the real portal. See countries/qatar/government.py.
GOVERNMENT_SUBMISSION_TYPES = [
	{
		"submission_type_code": "QAT_QATARIZATION_REPORT",
		"submission_type_name": "Qatarization Workforce Report",
		"category": "Workforce",
		"reference_doctype": "Qatarization Profile",
		"generate_method": "gcc_hr.countries.qatar.government.generate_qatarization_report",
		"validate_method": "gcc_hr.countries.qatar.government.validate_qatarization_report",
		"portal_url": "https://www.mol.gov.qa",
		"portal_instructions": (
			"Download the generated report and file it through the Ministry of Labour's workforce "
			"reporting workflow (MOL does not expose a verified public API for this)."
		),
	},
	{
		"submission_type_code": "QAT_WPS_REPORT",
		"submission_type_name": "WPS Registration Worksheet",
		"category": "Registration",
		"reference_doctype": "Qatar Employee Profile",
		"generate_method": "gcc_hr.countries.qatar.government.generate_wps_report",
		"validate_method": "gcc_hr.countries.qatar.government.validate_wps_report",
		"portal_url": "https://www.qcb.gov.qa",
		"portal_instructions": (
			"Use the worksheet to register each unregistered employee's salary payment through your "
			"bank's WPS integration, then come back and mark this submission Submitted."
		),
	},
]


def setup(company=None):
	create_document_types()
	create_compliance_rules()
	create_gratuity_rules()
	create_qatarization_requirement()
	create_government_submission_types()
	frappe.db.set_value("HR Country Settings", "Qatar", "compliance_engine_enabled", 1)
	if company:
		ensure_qatarization_profile(company)


def uninstall():
	# Conservative, like Saudi's own uninstall: disable the engine, don't
	# delete Document Types/Rules/Gratuity Rules that other records may
	# already reference.
	frappe.db.set_value("HR Country Settings", "Qatar", "compliance_engine_enabled", 0)


def create_document_types():
	for document_type_name in DOCUMENT_TYPES:
		name = f"Qatar-{document_type_name}"
		if frappe.db.exists("HR Document Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "HR Document Type",
				"country": "Qatar",
				"document_type_name": document_type_name,
				"requires_government_verification": document_type_name in ("QID", "Work Permit", "Visa"),
			}
		).insert(ignore_permissions=True)


def create_compliance_rules():
	for rule in COMPLIANCE_RULES:
		if frappe.db.exists("HR Compliance Rule", rule["rule_code"]):
			continue
		frappe.get_doc({"doctype": "HR Compliance Rule", "country": "Qatar", "enabled": 1, **rule}).insert(
			ignore_permissions=True
		)


def create_gratuity_rules():
	for rule in GRATUITY_RULES:
		if frappe.db.exists("Gratuity Rule", rule["name"]):
			continue
		frappe.get_doc({"doctype": "Gratuity Rule", **rule}).insert(ignore_permissions=True, ignore_if_duplicate=True)


def create_qatarization_requirement():
	if frappe.db.exists(
		"Qatarization Requirement",
		{"company": ["in", ("", None)], "activity": ["in", ("", None)], "effective_from": "2024-01-01"},
	):
		return
	frappe.get_doc(
		{
			"doctype": "Qatarization Requirement",
			# Explicit "" -- same default-injection footgun as Saudization
			# Requirement (see that doctype's setup.py note); caught here
			# proactively instead of rediscovered.
			"company": "",
			"target_percentage": DEFAULT_QATARIZATION_TARGET,
			"effective_from": "2024-01-01",
			"description": QATARIZATION_SEED_DESCRIPTION,
		}
	).insert(ignore_permissions=True)


def ensure_qatarization_profile(company):
	from gcc_hr.countries.qatar.qatarization import recalculate

	recalculate(company)


def create_government_submission_types():
	for submission_type in GOVERNMENT_SUBMISSION_TYPES:
		if frappe.db.exists("Government Submission Type", submission_type["submission_type_code"]):
			continue
		frappe.get_doc(
			{"doctype": "Government Submission Type", "country": "Qatar", "is_active": 1, **submission_type}
		).insert(ignore_permissions=True)
