# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from gcc_hr.countries.united_arab_emirates.rules import (
	check_contract_active,
	check_contract_salary_match,
	check_eid_expiry,
	check_non_emirati_has_eid,
	check_passport_expiry,
	check_work_permit_expiry,
	check_wps_registered,
)

TEST_COMPANY = "_Test GCC UAE Rules Co"


class TestUAERules(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGURC",
					"default_currency": "AED",
					"country": "United Arab Emirates",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "United Arab Emirates"}
			).insert(ignore_permissions=True)

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

	def test_emirati_national_skips_eid_and_work_permit_checks(self):
		employee = self._make_employee("Test Emirati National")
		frappe.db.set_value("UAE Employee Profile", employee.name, "nationality_status", "Emirati")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		result, message, action = check_eid_expiry(employee.name, profile, None)
		self.assertEqual(result, "Passed")

		result, message, action = check_work_permit_expiry(employee.name, profile, None)
		self.assertEqual(result, "Passed")

		result, message, action = check_non_emirati_has_eid(employee.name, profile, None)
		self.assertEqual(result, "Passed")

	def test_eid_expiry_boundaries(self):
		employee = self._make_employee("Test EID Boundaries")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		result, message, action = check_eid_expiry(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertIn("No EID expiry", message)

		frappe.db.set_value("UAE Employee Profile", employee.name, "eid_expiry", add_days(today(), 10))
		result, message, action = check_eid_expiry(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertTrue(action)

		frappe.db.set_value("UAE Employee Profile", employee.name, "eid_expiry", add_days(today(), -5))
		result, message, action = check_eid_expiry(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertIn("expired", message)

		frappe.db.set_value("UAE Employee Profile", employee.name, "eid_expiry", add_days(today(), 200))
		result, message, action = check_eid_expiry(employee.name, profile, None)
		self.assertEqual(result, "Passed")

	def test_work_permit_expiry_boundaries(self):
		employee = self._make_employee("Test Work Permit Boundaries")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		frappe.db.set_value("UAE Employee Profile", employee.name, "work_permit_expiry", add_days(today(), -1))
		result, message, action = check_work_permit_expiry(employee.name, profile, None)
		self.assertEqual(result, "Failed")
		self.assertIn("expired", message)

		frappe.db.set_value("UAE Employee Profile", employee.name, "work_permit_expiry", add_days(today(), 200))
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

	def test_full_engine_run_includes_uae_rules(self):
		from gcc_hr.gcc_hr_core.compliance_engine.engine import run_compliance_check

		employee = self._make_employee("Test Full Engine Run")
		check = run_compliance_check(employee.name, reason="Test")
		rule_codes = {r.rule for r in check.results}
		for rule_code in (
			"UAE_EID_EXPIRY",
			"UAE_WORK_PERMIT_EXPIRY",
			"UAE_PASSPORT_EXPIRY",
			"UAE_NON_EMIRATI_EID_ON_FILE",
			"UAE_CONTRACT_ACTIVE",
			"UAE_CONTRACT_SALARY_MATCH",
			"UAE_WPS_REGISTERED",
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

	def test_wps_registered_fails_by_default_and_passes_when_registered(self):
		employee = self._make_employee("Test WPS Registered Rule")
		profile = frappe.get_doc("Employee Compliance Profile", employee.name)

		result, message, action = check_wps_registered(employee.name, profile, None)
		self.assertEqual(result, "Failed")

		frappe.db.set_value("UAE Employee Profile", employee.name, "wps_registered", 1)
		result, message, action = check_wps_registered(employee.name, profile, None)
		self.assertEqual(result, "Passed")
