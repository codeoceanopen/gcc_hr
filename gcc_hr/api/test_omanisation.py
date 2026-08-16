# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.api.omanisation import recalculate_now, simulate

TEST_COMPANY = "_Test GCC Omanisation API Co"


class TestOmanisationAPI(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "Company", "company_name": TEST_COMPANY, "abbr": "TGOAC", "default_currency": "OMR", "country": "Oman"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Oman"}).insert(
				ignore_permissions=True
			)

	def test_recalculate_now_returns_profile_name(self):
		frappe.set_user("Administrator")
		name = recalculate_now(TEST_COMPANY)
		self.assertEqual(name, TEST_COMPANY)

	def test_simulate_api_returns_projection_dict(self):
		frappe.set_user("Administrator")
		result = simulate(TEST_COMPANY, hire_omani="2", hire_non_omani="0", terminate_omani="0", terminate_non_omani="0")
		self.assertIn("projected_percentage", result)
		self.assertIn("target_percentage", result)

	def test_recalculate_now_rejects_non_oman_company(self):
		# UI visibility is not security -- the API layer must independently
		# reject a company that isn't configured for Oman, even though the
		# permission check above passes.
		frappe.set_user("Administrator")
		other_company = "_Test GCC Non-Oman API Co"
		if not frappe.db.exists("Company", other_company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": other_company,
					"abbr": "TGNOA",
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", other_company):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": other_company, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

		with self.assertRaises(frappe.ValidationError):
			recalculate_now(other_company)

		with self.assertRaises(frappe.ValidationError):
			simulate(other_company, hire_omani="1", hire_non_omani="0", terminate_omani="0", terminate_non_omani="0")
