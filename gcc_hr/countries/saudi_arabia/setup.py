# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Saudi Arabia's setup()/uninstall() -- dispatched by
gcc_hr_core/doctype/gcc_hr_company_settings/gcc_hr_company_settings.py's
run_country_setup() whenever a company's country is set to Saudi Arabia, and
by gcc_hr/patches/v0_0/setup_saudi_arabia.py for companies already pointed
at Saudi Arabia before this module existed. Idempotent, like
hrms/regional/<country>/setup.py."""

import frappe

DOCUMENT_TYPES = [
	"Iqama",
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
		"rule_code": "SA_IQAMA_EXPIRY",
		"rule_name": "Iqama Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.saudi_arabia.rules.check_iqama_expiry",
	},
	{
		"rule_code": "SA_WORK_PERMIT_EXPIRY",
		"rule_name": "Work Permit Expiry",
		"category": "Document",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.saudi_arabia.rules.check_work_permit_expiry",
	},
	{
		"rule_code": "SA_PASSPORT_EXPIRY",
		"rule_name": "Passport Expiry",
		"category": "Document",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.saudi_arabia.rules.check_passport_expiry",
	},
	{
		"rule_code": "SA_NON_SAUDI_IQAMA_ON_FILE",
		"rule_name": "Non-Saudi Employee Has Iqama On File",
		"category": "Employee",
		"severity": "Blocking",
		"check_method": "gcc_hr.countries.saudi_arabia.rules.check_non_saudi_has_iqama",
	},
	{
		"rule_code": "SA_CONTRACT_ACTIVE",
		"rule_name": "Employment Contract Active",
		"category": "Contract",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.saudi_arabia.rules.check_contract_active",
	},
	{
		"rule_code": "SA_CONTRACT_SALARY_MATCH",
		"rule_name": "Contract vs Payroll Salary Match",
		"category": "Payroll",
		"severity": "Critical",
		"check_method": "gcc_hr.countries.saudi_arabia.rules.check_contract_salary_match",
	},
	{
		"rule_code": "SA_GOSI_REGISTERED",
		"rule_name": "GOSI Registered",
		"category": "Payroll",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.saudi_arabia.rules.check_gosi_registered",
	},
	{
		"rule_code": "SA_ANNUAL_LEAVE_ENTITLEMENT",
		"rule_name": "Annual Leave Entitlement (KSA Labour Law Art. 109)",
		"category": "Employee",
		"severity": "Warning",
		"check_method": "gcc_hr.countries.saudi_arabia.rules.check_annual_leave_entitlement",
	},
]

# KSA Labour Law Art. 109: 21 calendar days/year before 5 years of service,
# 30 calendar days/year from the 5th year onward (see countries/saudi_arabia/
# leave.py's get_annual_leave_entitlement). HRMS's Leave Type is a single
# flat allocation, not tenure-varying, so this seeds one Leave Type at the
# higher (30-day) ceiling and the SA_ANNUAL_LEAVE_ENTITLEMENT compliance rule
# flags any employee whose actual allocation falls short of their own
# tenure-appropriate entitlement -- the allocation amount itself is still an
# HR decision per Leave Policy Assignment, not hard-enforced here.
# Carry-forward and encashment reuse HRMS's existing engine as-is (Leave
# Allocation.carry_forward, Leave Encashment) -- gcc_hr adds no parallel one.
LEAVE_TYPE = {
	"leave_type_name": "Saudi Annual Leave",
	"max_leaves_allowed": 30,
	"is_carry_forward": 1,
	"maximum_carry_forwarded_leaves": 30,
	# KSA practice: unused leave may accumulate for up to 2 years by
	# agreement before the employer can require it be used/encashed.
	"expire_carry_forwarded_leaves_after_days": 730,
	"allow_encashment": 1,
	"max_encashable_leaves": 30,
	"non_encashable_leaves": 5,
	"earning_component": "Basic",
}

# KSA Labour Law Art. 84: half a month's wage for each of the first five
# years of service, one full month's wage for each year after that. On
# resignation the award is reduced: none under 2 years, 1/3 from 2-5 years,
# 2/3 from 5-10 years, full award at 10+ years. Modelled the same way
# hrms/regional/united_arab_emirates/setup.py models UAE's equivalent: one
# Gratuity Rule per HR-selected scenario, slabs expressed as a fraction of a
# 30-day month's wage per year of service.
GRATUITY_RULES = [
	{
		"name": "Saudi Arabia - Full Award (Termination/Retirement/Contract End)",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 0,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 5, "fraction_of_applicable_earnings": 15 / 30},
			{"from_year": 5, "to_year": 0, "fraction_of_applicable_earnings": 1},
		],
	},
	{
		"name": "Saudi Arabia - Resignation 2-5 Years (1/3 Award)",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 2,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 5, "fraction_of_applicable_earnings": (15 / 30) * (1 / 3)},
		],
	},
	{
		"name": "Saudi Arabia - Resignation 5-10 Years (2/3 Award)",
		"calculate_gratuity_amount_based_on": "Sum of all previous slabs",
		"work_experience_calculation_function": "Take Exact Completed Years",
		"minimum_year_for_gratuity": 5,
		"gratuity_rule_slabs": [
			{"from_year": 0, "to_year": 5, "fraction_of_applicable_earnings": (15 / 30) * (2 / 3)},
			{"from_year": 5, "to_year": 10, "fraction_of_applicable_earnings": 1 * (2 / 3)},
		],
	},
	{
		"name": "Saudi Arabia - Resignation 10+ Years (Full Award)",
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
	# award on Basic salary, same component UAE's own seeded rules imply.
	_rule["applicable_earnings_component"] = [{"salary_component": "Basic"}]

# Illustrative starting point only -- see GOSI Settings.description on each
# seeded row. Verify against the official GOSI circular in force before
# relying on these for real payroll; GOSI's contribution-base composition
# and rates have changed by phased reform (e.g. from July 2024) and this app
# never hard-codes a claim of current official rates.
GOSI_SETTINGS = [
	{
		"applicable_employee_category": "Saudi",
		"effective_from": "2024-07-01",
		"employee_contribution_rate": 9.75,
		"employer_contribution_rate": 11.75,
		"contribution_floor": 1500,
		"contribution_ceiling": 45000,
	},
	{
		"applicable_employee_category": "Non-Saudi",
		"effective_from": "2024-07-01",
		"employee_contribution_rate": 0,
		"employer_contribution_rate": 2,
		"contribution_floor": 400,
		"contribution_ceiling": 45000,
	},
]

SEED_DESCRIPTION = (
	"Seeded illustrative starting value -- verify against the official GOSI circular "
	"in force for this effective date before relying on this for real payroll."
)

# Nitaqat's actual required percentage varies heavily by activity and
# establishment size (roughly 5%-40%+) and changes by MHRSD decree -- this
# single global-fallback row is a round, clearly-illustrative placeholder,
# not a claim of any real sector's requirement. See Saudization
# Requirement.description on the seeded row, and add real activity/size-
# specific rows before relying on this for workforce-planning decisions.
DEFAULT_SAUDIZATION_TARGET = 25.0

SAUDIZATION_SEED_DESCRIPTION = (
	"Seeded illustrative global fallback -- Nitaqat's real required percentage varies by "
	"economic activity and establishment size. Add activity/business-size-specific rows "
	"(or a company-specific override) before relying on this for real compliance decisions."
)

# Neither submission type calls, or pretends to call, a real government API
# (MHRSD/Nitaqat and GOSI don't expose a verified public one) -- both just
# turn data this app already tracks into a document a human takes to the
# real portal. See gcc_hr_core/government.py's module docstring.
GOVERNMENT_SUBMISSION_TYPES = [
	{
		"submission_type_code": "SA_NITAQAT_REPORT",
		"submission_type_name": "Nitaqat Saudization Report",
		"category": "Workforce",
		"reference_doctype": "Saudization Profile",
		"generate_method": "gcc_hr.countries.saudi_arabia.government.generate_nitaqat_report",
		"validate_method": "gcc_hr.countries.saudi_arabia.government.validate_nitaqat_report",
		"portal_url": "https://mhrsd.gov.sa",
		"portal_instructions": (
			"Download the generated report and file it through the Nitaqat portal's workforce "
			"reporting workflow (MHRSD does not expose a verified public API for this)."
		),
	},
	{
		"submission_type_code": "SA_GOSI_REGISTRATION",
		"submission_type_name": "GOSI Registration Worksheet",
		"category": "Registration",
		"reference_doctype": "GOSI Employee Profile",
		"generate_method": "gcc_hr.countries.saudi_arabia.government.generate_gosi_registration_summary",
		"validate_method": "gcc_hr.countries.saudi_arabia.government.validate_gosi_registration_summary",
		"portal_url": "https://gosi.gov.sa",
		"portal_instructions": (
			"Use the worksheet to register each unregistered employee through the GOSI portal, "
			"then come back and mark this submission Submitted with GOSI's confirmation number."
		),
	},
]


def setup(company=None):
	create_document_types()
	create_compliance_rules()
	create_gratuity_rules()
	create_gosi_settings()
	create_saudization_requirement()
	create_government_submission_types()
	create_leave_type()
	frappe.db.set_value("HR Country Settings", "Saudi Arabia", "compliance_engine_enabled", 1)
	if company:
		ensure_saudization_profile(company)


def uninstall():
	# Conservative, like hrms's own regional uninstall: disable the engine,
	# don't delete Document Types/Rules/Gratuity Rules/GOSI Settings that
	# other records (Compliance Documents/Checks, Gratuity, GOSI Payroll
	# Calculation) may already reference.
	frappe.db.set_value("HR Country Settings", "Saudi Arabia", "compliance_engine_enabled", 0)


def create_document_types():
	for document_type_name in DOCUMENT_TYPES:
		name = f"Saudi Arabia-{document_type_name}"
		if frappe.db.exists("HR Document Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "HR Document Type",
				"country": "Saudi Arabia",
				"document_type_name": document_type_name,
				"requires_government_verification": document_type_name
				in ("Iqama", "Work Permit", "Visa"),
			}
		).insert(ignore_permissions=True)


def create_compliance_rules():
	for rule in COMPLIANCE_RULES:
		if frappe.db.exists("HR Compliance Rule", rule["rule_code"]):
			continue
		frappe.get_doc({"doctype": "HR Compliance Rule", "country": "Saudi Arabia", "enabled": 1, **rule}).insert(
			ignore_permissions=True
		)


def create_gratuity_rules():
	for rule in GRATUITY_RULES:
		if frappe.db.exists("Gratuity Rule", rule["name"]):
			continue
		frappe.get_doc({"doctype": "Gratuity Rule", **rule}).insert(ignore_permissions=True, ignore_if_duplicate=True)


def create_gosi_settings():
	for setting in GOSI_SETTINGS:
		if frappe.db.exists(
			"GOSI Settings",
			{"applicable_employee_category": setting["applicable_employee_category"], "effective_from": setting["effective_from"]},
		):
			continue
		frappe.get_doc({"doctype": "GOSI Settings", "description": SEED_DESCRIPTION, **setting}).insert(
			ignore_permissions=True
		)


def create_saudization_requirement():
	if frappe.db.exists(
		"Saudization Requirement",
		{"company": ["in", ("", None)], "activity": ["in", ("", None)], "effective_from": "2024-01-01"},
	):
		return
	frappe.get_doc(
		{
			"doctype": "Saudization Requirement",
			# Explicit "" rather than omitting the field -- Frappe auto-fills
			# any field literally named "company" with the current user's
			# default company when it's absent from the insert dict, which
			# would silently defeat this row's job as the blank/global
			# fallback (discovered by seeding into a site that had one).
			"company": "",
			"target_percentage": DEFAULT_SAUDIZATION_TARGET,
			"effective_from": "2024-01-01",
			"description": SAUDIZATION_SEED_DESCRIPTION,
		}
	).insert(ignore_permissions=True)


def ensure_saudization_profile(company):
	from gcc_hr.countries.saudi_arabia.saudization import recalculate

	recalculate(company)


def create_leave_type():
	if frappe.db.exists("Leave Type", LEAVE_TYPE["leave_type_name"]):
		return
	frappe.get_doc({"doctype": "Leave Type", **LEAVE_TYPE}).insert(ignore_permissions=True)


def create_government_submission_types():
	for submission_type in GOVERNMENT_SUBMISSION_TYPES:
		if frappe.db.exists("Government Submission Type", submission_type["submission_type_code"]):
			continue
		frappe.get_doc(
			{"doctype": "Government Submission Type", "country": "Saudi Arabia", "is_active": 1, **submission_type}
		).insert(ignore_permissions=True)
