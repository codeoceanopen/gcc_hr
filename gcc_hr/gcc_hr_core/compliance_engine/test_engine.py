# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.gcc_hr_core.compliance_engine.engine import run_compliance_check
from gcc_hr.gcc_hr_core.compliance_engine.expiry_engine import compute_status_for_document
from gcc_hr.gcc_hr_core.compliance_engine.scoring import calculate_score, get_status_for_score

# These tests need a country with zero *applicable* HR Compliance Rule
# rows, to isolate "engine behavior with no applicable rules" from any real
# country's ruleset. Through Phase 9 this worked by picking whichever GCC
# country was still an unimplemented placeholder (Qatar, then UAE, then
# Oman, then Bahrain -- each broke the moment the next phase seeded that
# country's real rules). Phase 10 (Kuwait) shipped the sixth and last GCC
# country, so there is no longer any placeholder country left to borrow --
# HR Country Settings' own validation only accepts the 6 real GCC countries
# (see test_non_gcc_country_rejected), so a fictional country isn't an
# option either. From here on, setUpClass disables Bahrain's real rules for
# the duration of this test class instead (restored via addClassCleanup),
# rather than relying on a country having none to begin with.
TEST_COMPANY = "_Test GCC Engine Co"
TEST_COUNTRY = "Bahrain"


def always_pass(employee, profile, rule):
	return ("Passed", "OK", "")


def always_fail_critical(employee, profile, rule):
	return ("Failed", "Test rule always fails.", "Fix the test condition.")


class TestComplianceEngine(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# Disable Bahrain's real seeded rules for the duration of this test
		# class -- see the module docstring above for why a placeholder
		# country is no longer available. Restored afterwards so this
		# doesn't affect any other test that happens to run in the same
		# process/transaction.
		disabled_rules = frappe.get_all(
			"HR Compliance Rule", filters={"country": TEST_COUNTRY, "enabled": 1}, pluck="name"
		)
		if disabled_rules:
			frappe.db.set_value("HR Compliance Rule", {"name": ["in", disabled_rules]}, "enabled", 0)

			def _restore_rules():
				frappe.db.set_value("HR Compliance Rule", {"name": ["in", disabled_rules]}, "enabled", 1)

			cls.addClassCleanup(_restore_rules)

		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGEC",
					"default_currency": "BHD",
					"country": TEST_COUNTRY,
				}
			).insert(ignore_permissions=True)

		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": TEST_COUNTRY}
			).insert(ignore_permissions=True)

		if not frappe.db.exists("Employee", {"company": TEST_COMPANY, "first_name": "Test Engine Employee"}):
			cls.employee = frappe.get_doc(
				{
					"doctype": "Employee",
					"first_name": "Test Engine Employee",
					"company": TEST_COMPANY,
					"date_of_birth": "1990-01-01",
					"date_of_joining": "2024-01-01",
					"gender": "Male",
				}
			).insert(ignore_permissions=True)
		else:
			cls.employee = frappe.get_doc(
				"Employee", frappe.db.get_value("Employee", {"company": TEST_COMPANY}, "name")
			)

	def setUp(self):
		frappe.db.delete("HR Compliance Rule", {"country": TEST_COUNTRY, "rule_code": ["like", "TEST_%"]})

	def test_employee_compliance_profile_auto_created(self):
		self.assertTrue(frappe.db.exists("Employee Compliance Profile", self.employee.name))
		profile = frappe.get_doc("Employee Compliance Profile", self.employee.name)
		self.assertEqual(profile.country, TEST_COUNTRY)

	def test_compliance_check_with_no_rules_scores_100(self):
		check = run_compliance_check(self.employee.name, reason="Test")
		self.assertEqual(check.compliance_score, 100)
		self.assertEqual(check.status, "Compliant")

	def test_compliance_check_with_failing_critical_rule(self):
		frappe.get_doc(
			{
				"doctype": "HR Compliance Rule",
				"rule_code": "TEST_ALWAYS_FAIL",
				"rule_name": "Always Fails (test)",
				"country": TEST_COUNTRY,
				"category": "Employee",
				"severity": "Critical",
				"check_method": "gcc_hr.gcc_hr_core.compliance_engine.test_engine.always_fail_critical",
			}
		).insert(ignore_permissions=True)

		check = run_compliance_check(self.employee.name, reason="Test")
		self.assertEqual(check.compliance_score, 80)  # 100 - 20 (Critical)
		self.assertEqual(check.critical_issues, 1)
		self.assertEqual(len(check.results), 1)
		self.assertEqual(check.results[0].result, "Failed")

		profile = frappe.get_doc("Employee Compliance Profile", self.employee.name)
		self.assertEqual(profile.compliance_score, 80)
		self.assertEqual(profile.compliance_status, "Compliant")  # 80 is still in the 75-89 band

	def test_compliance_rule_rejects_unimportable_check_method(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "HR Compliance Rule",
					"rule_code": "TEST_BAD_METHOD",
					"rule_name": "Bad Method (test)",
					"country": TEST_COUNTRY,
					"category": "Employee",
					"severity": "Warning",
					"check_method": "gcc_hr.does_not_exist.nope",
				}
			).insert(ignore_permissions=True)

	def test_scoring_bands(self):
		self.assertEqual(calculate_score([]), 100)
		self.assertEqual(calculate_score([{"severity": "Critical"}]), 80)
		self.assertEqual(get_status_for_score(95, "Saudi Arabia"), "Compliant")
		self.assertEqual(get_status_for_score(60, "Saudi Arabia"), "Warning")
		self.assertEqual(get_status_for_score(20, "Saudi Arabia"), "Critical")

	def test_document_expiry_status(self):
		from frappe.utils import add_days, today

		status, days_remaining, severity = compute_status_for_document(add_days(today(), 5))
		self.assertEqual(status, "Expiring Soon")
		self.assertEqual(days_remaining, 5)
		self.assertEqual(severity, "Critical")

		status, days_remaining, severity = compute_status_for_document(add_days(today(), -1))
		self.assertEqual(status, "Expired")
		self.assertEqual(severity, "Blocking")

		status, days_remaining, severity = compute_status_for_document(add_days(today(), 200))
		self.assertEqual(status, "Valid")
