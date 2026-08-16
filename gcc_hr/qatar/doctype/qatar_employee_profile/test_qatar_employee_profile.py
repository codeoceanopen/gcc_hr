# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

TEST_COMPANY = "_Test GCC Qatar Employee Co"


class TestQatarEmployeeProfile(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGQEC",
					"default_currency": "QAR",
					"country": "Qatar",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Qatar"}
			).insert(ignore_permissions=True)

	def test_auto_created_for_qatar_company_employee(self):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Qatar Sync Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Qatar Employee Profile", employee.name))

	def test_not_created_for_non_qatar_company_employee(self):
		other_company = "_Test GCC Non Qatar Co"
		if not frappe.db.exists("Company", other_company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": other_company,
					"abbr": "TGNQC",
					"default_currency": "USD",
				}
			).insert(ignore_permissions=True)
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Non Qatar Employee",
				"company": other_company,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Female",
			}
		).insert(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Qatar Employee Profile", employee.name))

	def test_missing_qid_is_a_soft_compliance_signal_not_a_hard_block(self):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test QID Signal Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)
		profile = frappe.get_doc("Qatar Employee Profile", employee.name)
		self.assertEqual(profile.nationality_status, "Non-Qatari")
		self.assertFalse(profile.qid_number)
		profile.save(ignore_permissions=True)  # must not raise

		from gcc_hr.countries.qatar.rules import check_non_qatari_has_qid

		result, message, action = check_non_qatari_has_qid(employee.name, None, None)
		self.assertEqual(result, "Failed")
		self.assertTrue(action)
