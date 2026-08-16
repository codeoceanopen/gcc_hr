# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""UAE's setup()/uninstall() -- dispatched by
gcc_hr_core/doctype/gcc_hr_company_settings/gcc_hr_company_settings.py's
run_country_setup() whenever a company's country is set to United Arab
Emirates, and by gcc_hr/patches/v0_5/setup_uae.py for companies already
pointed at UAE before this module existed. Idempotent, mirrors
countries/qatar/setup.py's shape -- except for EOSB, see
create_gratuity_rules()'s docstring."""

import frappe

DOCUMENT_TYPES = [
	"EID",
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
		"rule_code": "UAE_EID_EXPIRY",
		"rule_name": "EID Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.united_arab_emirates.rules.check_eid_expiry",
	},
	{
		"rule_code": "UAE_WORK_PERMIT_EXPIRY",
		"rule_name": "Work Permit Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.united_arab_emirates.rules.check_work_permit_expiry",
	},
	{
		"rule_code": "UAE_PASSPORT_EXPIRY",
		"rule_name": "Passport Expiry",
		"category": "Document",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.united_arab_emirates.rules.check_passport_expiry",
	},
	{
		"rule_code": "UAE_NON_EMIRATI_EID_ON_FILE",
		"rule_name": "Non-Emirati Employee Has EID On File",
		"category": "Employee",
		"severity": "Blocking",
		"check_method": "gcc_hr.countries.united_arab_emirates.rules.check_non_emirati_has_eid",
	},
	{
		"rule_code": "UAE_CONTRACT_ACTIVE",
		"rule_name": "Employment Contract Active",
		"category": "Contract",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.united_arab_emirates.rules.check_contract_active",
	},
	{
		"rule_code": "UAE_CONTRACT_SALARY_MATCH",
		"rule_name": "Contract vs Payroll Salary Match",
		"category": "Payroll",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.united_arab_emirates.rules.check_contract_salary_match",
	},
	{
		"rule_code": "UAE_WPS_REGISTERED",
		"rule_name": "WPS Registered",
		"category": "Payroll",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.united_arab_emirates.rules.check_wps_registered",
	},
]

# The three Gratuity Rule names hrms.regional.united_arab_emirates.setup.setup()
# creates -- see create_gratuity_rules()'s docstring for why this app reuses
# them instead of hand-rolling its own, unlike Saudi's and Qatar's EOSB rules.
UAE_GRATUITY_RULE_NAMES = [
	"Rule Under Limited Contract (UAE)",
	"Rule Under Unlimited Contract on termination (UAE)",
	"Rule Under Unlimited Contract on resignation (UAE)",
]

# UAE's Emiratisation quota (Cabinet Resolution: private-sector companies
# with 50+ skilled employees must raise skilled Emirati employment by a
# defined amount each year) is more concretely codified than Qatar's
# equivalent, but the exact scope/percentage/year still changes by decree --
# this seeded row is a round, illustrative placeholder, not a claim of the
# currently-mandated figure for any specific company. See Emiratisation
# Requirement.description on the seeded row.
DEFAULT_EMIRATISATION_TARGET = 10.0

EMIRATISATION_SEED_DESCRIPTION = (
	"Seeded illustrative global fallback -- UAE's Emiratisation quota varies by company size/"
	"activity and changes by Cabinet Resolution. Add activity/business-size-specific rows (or a "
	"company-specific override) before relying on this for real compliance decisions, and verify "
	"against current MOHRE guidance."
)

# Neither submission type calls, or pretends to call, a real government API
# (MOHRE and the Central Bank of the UAE don't expose a verified public one
# for these) -- both just turn data this app already tracks into a document
# a human takes to the real portal. See countries/united_arab_emirates/government.py.
GOVERNMENT_SUBMISSION_TYPES = [
	{
		"submission_type_code": "UAE_EMIRATISATION_REPORT",
		"submission_type_name": "Emiratisation Workforce Report",
		"category": "Workforce",
		"reference_doctype": "Emiratisation Profile",
		"generate_method": "gcc_hr.countries.united_arab_emirates.government.generate_emiratisation_report",
		"validate_method": "gcc_hr.countries.united_arab_emirates.government.validate_emiratisation_report",
		"portal_url": "https://www.mohre.gov.ae",
		"portal_instructions": (
			"Download the generated report and file it through MOHRE's Emiratisation reporting "
			"workflow (MOHRE does not expose a verified public API for this)."
		),
	},
	{
		"submission_type_code": "UAE_WPS_REPORT",
		"submission_type_name": "WPS Registration Worksheet",
		"category": "Registration",
		"reference_doctype": "UAE Employee Profile",
		"generate_method": "gcc_hr.countries.united_arab_emirates.government.generate_wps_report",
		"validate_method": "gcc_hr.countries.united_arab_emirates.government.validate_wps_report",
		"portal_url": "https://www.centralbank.ae",
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
	create_emiratisation_requirement()
	create_government_submission_types()
	frappe.db.set_value("HR Country Settings", "United Arab Emirates", "compliance_engine_enabled", 1)
	if company:
		ensure_emiratisation_profile(company)


def uninstall():
	frappe.db.set_value("HR Country Settings", "United Arab Emirates", "compliance_engine_enabled", 0)


def create_document_types():
	for document_type_name in DOCUMENT_TYPES:
		name = f"United Arab Emirates-{document_type_name}"
		if frappe.db.exists("HR Document Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "HR Document Type",
				"country": "United Arab Emirates",
				"document_type_name": document_type_name,
				"requires_government_verification": document_type_name in ("EID", "Work Permit", "Visa"),
			}
		).insert(ignore_permissions=True)


def create_compliance_rules():
	for rule in COMPLIANCE_RULES:
		if frappe.db.exists("HR Compliance Rule", rule["rule_code"]):
			continue
		frappe.get_doc({"doctype": "HR Compliance Rule", "country": "United Arab Emirates", "enabled": 1, **rule}).insert(
			ignore_permissions=True
		)


def create_gratuity_rules():
	"""UAE is the first country where Frappe HR itself already ships a
	regional EOSB implementation
	(hrms/regional/united_arab_emirates/setup.py, dispatched on
	Company.on_update via hrms's own, narrower regional mechanism -- see
	ARCHITECTURE.md's "UAE (Phase 7)" section) modelling the current UAE
	Labour Law (Federal Decree-Law No. 33 of 2021, Art. 51) slabs, including
	the resignation-reduction tiers this app deliberately didn't attempt for
	Qatar. Calling it directly here -- rather than hand-rolling a competing
	rule the way Saudi's and Qatar's setup.py had to, since HRMS has no
	Saudi/Qatar equivalent -- is reuse-over-duplicate in its most literal
	form, and doesn't depend on hrms's own dispatch having already fired
	(that only triggers on a Company's country *changing* on an existing
	document, not on insert, so relying on it would be fragile).

	hrms's own script has two bugs already discovered once before in this
	app's history (Saudi's own Gratuity Rule seeding, Phase 3): it sets a
	stale/renamed field (`work_experience_calculation_method`, silently
	dropped by Frappe -- correct name `work_experience_calculation_function`)
	and never sets the mandatory `applicable_earnings_component`, working
	only because it inserts with `ignore_mandatory=True`. Fixed up here on
	the rows hrms's setup() creates, the same way Phase 3 fixed its own
	rules -- this app's code stays correct even though the bug is in hrms's,
	which is out of scope to edit directly.
	"""
	frappe.get_attr("hrms.regional.united_arab_emirates.setup.setup")()

	for name in UAE_GRATUITY_RULE_NAMES:
		if not frappe.db.exists("Gratuity Rule", name):
			continue
		rule = frappe.get_doc("Gratuity Rule", name)
		changed = False
		if rule.work_experience_calculation_function != "Take Exact Completed Years":
			rule.work_experience_calculation_function = "Take Exact Completed Years"
			changed = True
		if not rule.applicable_earnings_component:
			rule.append("applicable_earnings_component", {"salary_component": "Basic"})
			changed = True
		if changed:
			rule.save(ignore_permissions=True)


def create_emiratisation_requirement():
	if frappe.db.exists(
		"Emiratisation Requirement",
		{"company": ["in", ("", None)], "activity": ["in", ("", None)], "effective_from": "2024-01-01"},
	):
		return
	frappe.get_doc(
		{
			"doctype": "Emiratisation Requirement",
			# Explicit "" -- same default-injection footgun as Saudization/
			# Qatarization Requirement (see those doctypes' setup.py notes).
			"company": "",
			"target_percentage": DEFAULT_EMIRATISATION_TARGET,
			"effective_from": "2024-01-01",
			"description": EMIRATISATION_SEED_DESCRIPTION,
		}
	).insert(ignore_permissions=True)


def ensure_emiratisation_profile(company):
	from gcc_hr.countries.united_arab_emirates.emiratisation import recalculate

	recalculate(company)


def create_government_submission_types():
	for submission_type in GOVERNMENT_SUBMISSION_TYPES:
		if frappe.db.exists("Government Submission Type", submission_type["submission_type_code"]):
			continue
		frappe.get_doc(
			{"doctype": "Government Submission Type", "country": "United Arab Emirates", "is_active": 1, **submission_type}
		).insert(ignore_permissions=True)
