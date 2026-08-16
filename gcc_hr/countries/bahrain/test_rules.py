# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from gcc_hr.countries.bahrain.rules import (
	check_contract_active,
	check_contract_salary_match,
	check_cpr_expiry,
	check_non_bahraini_has_cpr,
	check_passport_expiry,
	check_sio_registered,
	check_work_permit_expiry,
)

TEST_COMPANY = "_Test GCC Bahrain Rules Co"


class TestBahrainRules(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGBRC",
					"default_currency": "BHD",
					"country": "Bahrain",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Bahrain"}).insert(
				ignore_permissions=True
			)

	def _make_employee(self, label):
		return frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": label,
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)

	def test_bahraini_national_skips_cpr_and_work_permit_checks(self):
		employee = self._make_employee("Test Bahraini National")
		frappe.db.set_value("Bahrain Employee Profile", employee.name, "nationality_status", "Bahraini")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		result, message, action = check_cpr_expiry(employee.name, profile, None)
		self.assertEqual(result, "Passed")

		result, message, action = check_work_permit_expiry(employee.name, profile, None)
		self.assertEqual(result, "Passed")

		result, message, action = check_non_bahraini_has_cpr(employee.name, profile, None)
		self.assertEqual(result, "Passed")

	def test_cpr_expiry_boundaries(self):
		employee = self._make_employee("Test CPR Boundaries")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		result, message, action = check_cpr_expiry(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertIn("No CPR expiry", message)

		frappe.db.set_value("Bahrain Employee Profile", employee.name, "cpr_expiry", add_days(today(), -5))
		result, message, action = check_cpr_expiry(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertIn("expired", message)

		frappe.db.set_value("Bahrain Employee Profile", employee.name, "cpr_expiry", add_days(today(), 200))
		result, message, action = check_cpr_expiry(employee.name, profile, None)
		self.assertEqual(result, "Passed")

	def test_work_permit_expiry_boundaries(self):
		employee = self._make_employee("Test Work Permit Boundaries")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		frappe.db.set_value("Bahrain Employee Profile", employee.name, "work_permit_expiry", add_days(today(), -1))
		result, message, action = check_work_permit_expiry(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertIn("expired", message)

		frappe.db.set_value("Bahrain Employee Profile", employee.name, "work_permit_expiry", add_days(today(), 200))
		result, message, action = check_work_permit_expiry(employee.name, profile, None)
		self.assertEqual(result, "Passed")

	def test_passport_expiry_uses_employee_compliance_profile_directly(self):
		employee = self._make_employee("Test Passport Boundaries")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		result, message, action = check_passport_expiry(employee.name, profile, None)
		self.assertEqual(result, "Skipped")

		frappe.db.set_value("Employee", employee.name, "valid_upto", add_days(today(), 30))
		profile.save(ignore_permissions=True)
		result, message, action = check_passport_expiry(employee.name, profile, None)
		self.assertEqual(result, "Failed")

		frappe.db.set_value("Employee", employee.name, "valid_upto", add_days(today(), 400))
		profile.save(ignore_permissions=True)
		result, message, action = check_passport_expiry(employee.name, profile, None)
		self.assertEqual(result, "Passed")

	def test_full_engine_run_includes_bahrain_rules(self):
		from gcc_hr.gcc_hr_core.compliance_engine.engine import run_compliance_check

		employee = self._make_employee("Test Full Engine Run")
		check = run_compliance_check(employee.name, reason="Test")
		rule_codes = {r.rule for r in check.results}
		for rule_code in (
			"BAH_CPR_EXPIRY",
			"BAH_WORK_PERMIT_EXPIRY",
			"BAH_PASSPORT_EXPIRY",
			"BAH_NON_BAHRAINI_CPR_ON_FILE",
			"BAH_CONTRACT_ACTIVE",
			"BAH_CONTRACT_SALARY_MATCH",
			"BAH_SIO_REGISTERED",
		):
			self.assertIn(rule_code, rule_codes)
		self.assertEqual(check.critical_issues, 4)
		self.assertEqual(check.warnings, 1)

	def test_contract_active_fails_without_a_linked_contract(self):
		employee = self._make_employee("Test No Contract")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)
		result, message, action = check_contract_active(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertTrue(action)

	def test_contract_active_fails_when_contract_expired(self):
		employee = self._make_employee("Test Expired Contract")
		contract = frappe.get_doc(
			{
				"doctype": "Contract",
				"party_type": "Employee",
				"party_name": employee.name,
				"start_date": "2020-01-01",
				"end_date": add_days(today(), -10),
				"contract_terms": "Test contract.",
				"gcc_basic_salary": 5000,
			}
		)
		contract.insert(ignore_permissions=True)
		contract.submit()
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)
		profile.contract = contract.name
		profile.save(ignore_permissions=True)

		result, message, action = check_contract_active(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertIn("expired", message)

	def test_contract_active_passes_for_active_submitted_contract(self):
		employee = self._make_employee("Test Active Contract")
		contract = frappe.get_doc(
			{
				"doctype": "Contract",
				"party_type": "Employee",
				"party_name": employee.name,
				"start_date": "2024-01-01",
				"end_date": add_days(today(), 365),
				"contract_terms": "Test contract.",
				"gcc_basic_salary": 5000,
			}
		)
		contract.insert(ignore_permissions=True)
		contract.submit()
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)
		profile.contract = contract.name
		profile.save(ignore_permissions=True)

		result, message, action = check_contract_active(employee.name, profile, None)
		self.assertEqual(result, "Passed")

	def test_contract_salary_match_skips_without_salary_structure_assignment(self):
		employee = self._make_employee("Test Salary Match No Assignment")
		contract = frappe.get_doc(
			{
				"doctype": "Contract",
				"party_type": "Employee",
				"party_name": employee.name,
				"start_date": "2024-01-01",
				"contract_terms": "Test contract.",
				"gcc_basic_salary": 5000,
			}
		)
		contract.insert(ignore_permissions=True)
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)
		profile.contract = contract.name
		profile.save(ignore_permissions=True)

		result, message, action = check_contract_salary_match(employee.name, profile, None)
		self.assertEqual(result, "Skipped")

	def test_sio_registered_fails_by_default_and_passes_when_registered(self):
		employee = self._make_employee("Test SIO Registered Rule")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		result, message, action = check_sio_registered(employee.name, profile, None)
		self.assertEqual(result, "Failed")

		frappe.db.set_value("Bahrain Employee Profile", employee.name, "sio_registered", 1)
		result, message, action = check_sio_registered(employee.name, profile, None)
		self.assertEqual(result, "Passed")
