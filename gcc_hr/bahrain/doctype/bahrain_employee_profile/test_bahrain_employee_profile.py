# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

TEST_COMPANY = "_Test GCC Bahrain Employee Co"


class TestBahrainEmployeeProfile(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGBEC",
					"default_currency": "BHD",
					"country": "Bahrain",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Bahrain"}).insert(
				ignore_permissions=True
			)

	def test_auto_created_for_bahrain_company_employee(self):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Bahrain Sync Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Bahrain Employee Profile", employee.name))

	def test_not_created_for_non_bahrain_company_employee(self):
		other_company = "_Test GCC Non Bahrain Co"
		if not frappe.db.exists("Company", other_company):
			frappe.get_doc(
				{"doctype": "Company", "company_name": other_company, "abbr": "TGNBC", "default_currency": "USD"}
			).insert(ignore_permissions=True)
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Non Bahrain Employee",
				"company": other_company,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Female",
			}
		).insert(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Bahrain Employee Profile", employee.name))

	def test_missing_cpr_is_a_soft_compliance_signal_not_a_hard_block(self):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test CPR Signal Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)
		profile = frappe.get_doc("Bahrain Employee Profile", employee.name)
		self.assertEqual(profile.nationality_status, "Non-Bahraini")
		self.assertFalse(profile.cpr_number)
		profile.save(ignore_permissions=True)  # must not raise

		from gcc_hr.countries.bahrain.rules import check_non_bahraini_has_cpr

		result, message, action = check_non_bahraini_has_cpr(employee.name, None, None)
		self.assertEqual(result, "Failed")
		self.assertTrue(action)
