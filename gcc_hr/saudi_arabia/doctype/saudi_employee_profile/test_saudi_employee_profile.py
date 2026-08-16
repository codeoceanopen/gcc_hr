# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

TEST_COMPANY = "_Test GCC Saudi Employee Co"


class TestSaudiEmployeeProfile(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": TEST_COMPANY,
					"abbr": "TGSEC",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

	def test_auto_created_for_saudi_company_employee(self):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Saudi Sync Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Saudi Employee Profile", employee.name))

	def test_not_created_for_non_saudi_company_employee(self):
		# The default "glob" / other pre-existing companies in this bench have
		# no GCC HR Company Settings pointed at Saudi Arabia by default in a
		# fresh site, so a bare Employee under a company with no GCC HR
		# Company Settings at all must not get a Saudi Employee Profile.
		other_company = "_Test GCC Non Saudi Co"
		if not frappe.db.exists("Company", other_company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": other_company,
					"abbr": "TGNSC",
					"default_currency": "QAR",
				}
			).insert(ignore_permissions=True)
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Non Saudi Employee",
				"company": other_company,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Female",
			}
		).insert(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Saudi Employee Profile", employee.name))

	def test_missing_iqama_is_a_soft_compliance_signal_not_a_hard_block(self):
		# The profile is auto-created the moment a new hire's Employee record
		# is inserted, before HR necessarily has their Iqama yet -- a
		# save-blocking mandatory field would break that auto-provisioning
		# flow. `mandatory_depends_on` in the JSON is a Desk-only indicator
		# (Frappe never enforces it server-side); missing Iqama data is
		# instead caught by the SA_NON_SAUDI_IQAMA_ON_FILE compliance rule.
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test Iqama Signal Employee",
				"company": TEST_COMPANY,
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2024-01-01",
				"gender": "Male",
			}
		).insert(ignore_permissions=True)
		profile = frappe.get_doc("Saudi Employee Profile", employee.name)
		self.assertEqual(profile.nationality_status, "Non-Saudi")
		self.assertFalse(profile.iqama_number)
		profile.save(ignore_permissions=True)  # must not raise

		from gcc_hr.countries.saudi_arabia.rules import check_non_saudi_has_iqama

		result, message, action = check_non_saudi_has_iqama(employee.name, None, None)
		self.assertEqual(result, "Failed")
		self.assertTrue(action)
