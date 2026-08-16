# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.api.bahrainisation import recalculate_now, simulate

TEST_COMPANY = "_Test GCC Bahrainisation API Co"


class TestBahrainisationAPI(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "Company", "company_name": TEST_COMPANY, "abbr": "TGBAC", "default_currency": "BHD", "country": "Bahrain"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Bahrain"}).insert(
				ignore_permissions=True
			)

	def test_recalculate_now_returns_profile_name(self):
		frappe.set_user("Administrator")
		name = recalculate_now(TEST_COMPANY)
		self.assertEqual(name, TEST_COMPANY)

	def test_simulate_api_returns_projection_dict(self):
		frappe.set_user("Administrator")
		result = simulate(TEST_COMPANY, hire_bahraini="2", hire_non_bahraini="0", terminate_bahraini="0", terminate_non_bahraini="0")
		self.assertIn("projected_percentage", result)
		self.assertIn("target_percentage", result)

	def test_recalculate_now_rejects_company_configured_for_a_different_country(self):
		frappe.set_user("Administrator")
		company = "_Test GCC Bahrainisation API Wrong Country Co"
		if not frappe.db.exists("Company", company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company,
					"abbr": "TGBAW",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", company):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": company, "country": "Saudi Arabia"}).insert(
				ignore_permissions=True
			)

		self.assertRaises(frappe.ValidationError, recalculate_now, company)
		self.assertRaises(frappe.ValidationError, simulate, company, hire_bahraini="1")
