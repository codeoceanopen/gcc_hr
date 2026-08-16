# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from gcc_hr.api.saudization import get_gosi_summary, recalculate_now, simulate

TEST_COMPANY = "_Test GCC Saudization API Co"


class TestSaudizationAPI(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.db.exists("Company", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "Company", "company_name": TEST_COMPANY, "abbr": "TGSAC", "default_currency": "SAR", "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", TEST_COMPANY):
			frappe.get_doc(
				{"doctype": "GCC HR Company Settings", "company": TEST_COMPANY, "country": "Saudi Arabia"}
			).insert(ignore_permissions=True)

	def test_recalculate_now_returns_profile_name(self):
		frappe.set_user("Administrator")
		name = recalculate_now(TEST_COMPANY)
		self.assertEqual(name, TEST_COMPANY)

	def test_simulate_api_returns_projection_dict(self):
		frappe.set_user("Administrator")
		result = simulate(TEST_COMPANY, hire_saudi="2", hire_non_saudi="0", terminate_saudi="0", terminate_non_saudi="0")
		self.assertIn("projected_percentage", result)
		self.assertIn("target_percentage", result)

	def test_recalculate_now_rejects_wrong_country_company(self):
		# Backend enforcement: UI visibility alone must not be what stops a
		# Saudi-only API from being called against a non-Saudi company.
		frappe.set_user("Administrator")
		company = "_Test GCC Saudization API Wrong Country Co"
		if not frappe.db.exists("Company", company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company,
					"abbr": "TGSAW",
					"default_currency": "QAR",
					"country": "Qatar",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", company):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": company, "country": "Qatar"}).insert(
				ignore_permissions=True
			)

		self.assertRaises(frappe.ValidationError, recalculate_now, company)

	def test_simulate_rejects_wrong_country_company(self):
		frappe.set_user("Administrator")
		company = "_Test GCC Saudization API Wrong Country Co"
		if not frappe.db.exists("Company", company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company,
					"abbr": "TGSAW",
					"default_currency": "QAR",
					"country": "Qatar",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", company):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": company, "country": "Qatar"}).insert(
				ignore_permissions=True
			)

		self.assertRaises(frappe.ValidationError, simulate, company, hire_saudi="1")

	def test_get_gosi_summary_returns_status_dict(self):
		frappe.set_user("Administrator")
		result = get_gosi_summary(TEST_COMPANY)
		self.assertIn("counts", result)
		self.assertIn("status", result)

	def test_get_gosi_summary_rejects_wrong_country_company(self):
		frappe.set_user("Administrator")
		company = "_Test GCC Saudization API Wrong Country Co"
		if not frappe.db.exists("Company", company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company,
					"abbr": "TGSAW",
					"default_currency": "QAR",
					"country": "Qatar",
				}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("GCC HR Company Settings", company):
			frappe.get_doc({"doctype": "GCC HR Company Settings", "company": company, "country": "Qatar"}).insert(
				ignore_permissions=True
			)

		self.assertRaises(frappe.ValidationError, get_gosi_summary, company)
